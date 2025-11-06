

import base64

from lxml import etree, objectify
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..models.special_dict import CaselessDictionary

import zipfile
import io
import logging

_logger = logging.getLogger(__name__)

TYPE_CFDI22_TO_CFDI33 = {
    'ingreso': 'I',
    'egreso': 'E',
    'traslado': 'T',
    'nomina': 'N',
    'pago': 'P',
}


class AttachXmlsWizard(models.TransientModel):
    _name = 'multi.file.attach.xmls.wizard'
    _description = 'AttachXmlsWizard'
    
    dragndrop = fields.Char()

    xml_binary_file = fields.Binary(string="Zip File")

    @api.model
    def remove_wrong_file(self, files):
        wrong_file_dict = self.check_xml(files)
        remove_list = []
        if 'wrongfiles' in wrong_file_dict.keys():
            for key in wrong_file_dict['wrongfiles']:
                value_keys = wrong_file_dict['wrongfiles'][key].keys()
                if 'uuid_duplicated' in value_keys:
                    remove_list.append(key)
        return remove_list

    @staticmethod
    def _xml2capitalize(xml):
        """Receive 1 lxml etree object and change all attrib to Capitalize.
        """
        def recursive_lxml(element):
            for attrib, value in element.attrib.items():
                new_attrib = "%s%s" % (attrib[0].upper(), attrib[1:])
                element.attrib.update({new_attrib: value})

            for child in element.getchildren():
                child = recursive_lxml(child)
            return element
        return recursive_lxml(xml)

    @staticmethod
    def _l10n_mx_edi_convert_cfdi32_to_cfdi33(xml):
        """Convert a xml from cfdi32 to cfdi33
        :param xml: The xml 32 in lxml.objectify object
        :return: A xml 33 in lxml.objectify object
        """
        if xml.get('version', None) != '3.2':
            return xml
        # TODO: Process negative taxes "Retenciones" node
        # TODO: Process payment term
        xml = AttachXmlsWizard._xml2capitalize(xml)
        xml.attrib.update({
            'TipoDeComprobante': TYPE_CFDI22_TO_CFDI33[
                xml.attrib['tipoDeComprobante']],
            'Version': '3.3',
            'MetodoPago': 'PPD',
        })
        return xml

    
    @api.model
    def l10n_mx_edi_get_tfd_etree(self, cfdi):
        '''Get the TimbreFiscalDigital node from the cfdi.

        :param cfdi: The cfdi as etree
        :return: the TimbreFiscalDigital node
        '''
        if not hasattr(cfdi, 'Complemento'):
            return None
        attribute = 'tfd:TimbreFiscalDigital[1]'
        namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        for Complemento in cfdi.Complemento:
            node = Complemento.xpath(attribute, namespaces=namespace)
            if node:
                break
        return node[0] if node else None
    
    @api.model
    def check_xml(self, files, **kwargs):
        """ Validate that attributes in the xml before create invoice
        or attach xml in it
        :param files: dictionary of CFDIs in b64
        :type files: dict
        param account_id: The account by default that must be used in the
        lines of the invoice if this is created
        :type account_id: int
        :return: the Result of the CFDI validation
        :rtype: dict
        """
        if not isinstance(files, dict):
            raise UserError(_("Something went wrong. The parameter for XML "
                              "files must be a dictionary."))
        wrongfiles = {}
        attachments = {}
        attachment_uuids = {}
        attach_obj = self.env['ir.attachment']
        invoice_obj = self.env['account.move']
        payment_obj = self.env['account.payment']
        if 'currentCompanyId' in kwargs.get('ctx') and kwargs.get('ctx').get('currentCompanyId'):
            company = self.env['res.company'].browse(int(kwargs.get('ctx').get('currentCompanyId')))
        else:
            company = self.env.company
        company_vat = company.vat
        company_id = company.id
        NSMAP = {
                 'xsi':'http://www.w3.org/2001/XMLSchema-instance',
                 'cfdi':'http://www.sat.gob.mx/cfd/3', 
                 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
                 'pago10': 'http://www.sat.gob.mx/Pagos',
                 }
        for key, xml64 in files.items():
            try:
                if isinstance(xml64, bytes):
                    xml64 = xml64.decode()
                xml_str = base64.b64decode(xml64.replace('data:text/xml;base64,', ''))
                # Fix the CFDIs emitted by the SAT
                xml_str = xml_str.replace(b'xmlns:schemaLocation', b'xsi:schemaLocation')
                xml = objectify.fromstring(xml_str)
                tree = etree.fromstring(xml_str)
            except (AttributeError, SyntaxError) as exce:
                wrongfiles.update({key: {
                    'xml64': xml64, 'where': 'CheckXML',
                    'error': [exce.__class__.__name__, str(exce)]}})
                continue
            xml = self._l10n_mx_edi_convert_cfdi32_to_cfdi33(xml)
            xml_tfd = self.l10n_mx_edi_get_tfd_etree(xml)
            
            xml_uuid = False if xml_tfd is None else xml_tfd.get('UUID', '')
            
            if not xml_uuid:
                msg = {'signed': True, 'xml64': True}
                wrongfiles.update({key: msg})
                continue
            else:
                xml_uuid = xml_uuid.upper()

            cfdi_type = xml.get('TipoDeComprobante', 'I')
            receptor = xml.Receptor.attrib or {}
            receptor_rfc = receptor.get('Rfc','')
            if receptor_rfc == company_vat:
                cfdi_type = 'S'+cfdi_type
            
            try:
                ns = tree.nsmap
                ns.update({'re': 'http://exslt.org/regular-expressions'})
            except Exception:
                ns = {'re': 'http://exslt.org/regular-expressions'}
            
            cfdi_version = tree.get("Version",'4.0')
            if cfdi_version=='4.0':
                NSMAP.update({'cfdi':'http://www.sat.gob.mx/cfd/4', 'pago20': 'http://www.sat.gob.mx/Pagos20',})
            else:
                NSMAP.update({'cfdi':'http://www.sat.gob.mx/cfd/3', 'pago10': 'http://www.sat.gob.mx/Pagos',})
            
            if cfdi_type in ['I','E','P','N','T']:
                element_tag = 'Receptor'
            else:
                element_tag = 'Emisor'
            try:
                elements = tree.xpath("//*[re:test(local-name(), '%s','i')]"%(element_tag), namespaces=ns)
            except Exception:
                elements = None
            
            client_rfc, client_name = '', ''
            if elements:
                attrib_dict = CaselessDictionary(dict(elements[0].attrib))
                client_rfc = attrib_dict.get('rfc') 
                client_name = attrib_dict.get('nombre')

            monto_total = 0
            if cfdi_type=='P' or cfdi_type=='SP':

                Complemento = tree.findall('cfdi:Complemento', NSMAP)
                for complementos in Complemento:
                   if cfdi_version == '4.0':
                      pagos = complementos.find('pago20:Pagos', NSMAP)
                      pago = pagos.find('pago20:Totales', NSMAP)
                      monto_total = pago.attrib['MontoTotalPagos']
                   else:
                      pagos = complementos.find('pago10:Pagos', NSMAP)
                      try:
                         pago = pagos.find('pago10:Pago',NSMAP)
                         monto_total = pago.attrib['Monto']
                      except Exception as e:
                         for payment in pagos.find('pago10:Pago',NSMAP):
                            monto_total += float(payment.attrib['Monto'])
                   if pagos:
                       break
            else:
                monto_total = tree.get('Total', tree.get('total'))

            filename = xml_uuid + '.xml'
            vals = {
                    'cfdi_type' : cfdi_type,
                    'cfdi_uuid' : xml_uuid,
                    'rfc_tercero' : client_rfc,
                    'nombre_tercero' : client_name,
                    'cfdi_total' : monto_total, 
                    'date_cfdi' : tree.get('Fecha',tree.get('fecha')),
                    'serie_folio' : tree.get('Folio',tree.get('folio')),
                    'name' : filename,
                    'store_fname' : filename,
                    'datas' : xml64.replace('data:text/xml;base64,', ''),
                    'type' :'binary',
                    'company_id' :company_id,
                    }
            if cfdi_type=='SP' or cfdi_type=='P':
                    for uu in [xml_uuid,xml_uuid.lower(),xml_uuid.upper()]:
                        payment_exist = payment_obj.search([('l10n_mx_edi_cfdi_uuid_cusom','=',uu)],limit=1)
                        if payment_exist:
                            vals.update({'creado_en_odoo' : True,'payment_ids':[(6,0, payment_exist.ids)]})
                            break
            if cfdi_type=='SE' or cfdi_type=='E':
                    for uu in [xml_uuid,xml_uuid.lower(),xml_uuid.upper()]:
                        invoice_exist = invoice_obj.search([('l10n_mx_edi_cfdi_uuid_cusom','=',uu)],limit=1)
                        if invoice_exist:
                            vals.update({'creado_en_odoo' : True,'invoice_ids':[(6,0, invoice_exist.ids)]})
                            break
            else:
                    for uu in [xml_uuid,xml_uuid.lower(),xml_uuid.upper()]:
                        invoice_exist = invoice_obj.search([('l10n_mx_edi_cfdi_uuid_cusom','=',uu)],limit=1)
                        if invoice_exist:
                            vals.update({'creado_en_odoo' : True,'invoice_ids':[(6,0, invoice_exist.ids)]})
                            break
            attachment_uuids.update({xml_uuid : [vals, key]})

        attas = attach_obj.sudo().search([('cfdi_uuid','in',list(attachment_uuids.keys())), ('company_id', '=', company_id)])
        exist_uuids = dict([(att.cfdi_uuid, att.id) for att in attas]) #attas.mapped('cfdi_uuid')

        for uuid, data in attachment_uuids.items():
            key = data[1]
            if uuid in exist_uuids:
                attachments.update({key: {'attachment_id': exist_uuids.get(uuid)}})
                continue
            vals = data[0]
            #cfdi_type ='S'+cfdi_type
            attach_rec = attach_obj.create(vals)
            attachments.update({key: {'attachment_id': attach_rec.id}})
        
        return {'wrongfiles': wrongfiles,
                'attachments': attachments}

    def get_data_xml(self, **kwargs):
        # Lista para recopilar mensajes sobre archivos no procesados
        warning_messages = []
        for rec in self:
            attach_obj = self.env['ir.attachment']

            company = self.env.company
            company_vat = company.vat
            company_id = company.id
            
            xml_binary_file = self.xml_binary_file
            if xml_binary_file:
                data = base64.b64decode(xml_binary_file)
                zip_ref = zipfile.ZipFile(io.BytesIO(data))
                xml_filenames = [f for f in zip_ref.namelist() if f.lower().endswith('.xml')]
                
                if xml_filenames:
                    for x in xml_filenames:
                        _logger.info("Processing file: %s", x)
                        
                        # LEE el contenido del archivo
                        xml_file = zip_ref.read(x)

                        # --- INICIO DE LA SOLUCIÓN ---
                        # 1. Validar que el contenido del archivo no esté vacío
                        if not xml_file:
                            _logger.warning("Skipping empty file: %s", x)
                            continue

                        # 2. Manejar posibles errores de sintaxis XML
                        try:
                            # Intenta parsear el archivo
                            tree = etree.fromstring(xml_file)
                        except etree.XMLSyntaxError as e:
                            _logger.error("XMLSyntaxError processing file %s: %s", x, e)
                            continue
                        # --- FIN DE LA SOLUCIÓN ---
                        
                        
                        attribute = '//tfd:TimbreFiscalDigital'
                        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
                        rfc_emisor = tree.xpath('cfdi:Emisor', namespaces=namespaces)[0].get('Rfc')
                        name_emisor = tree.xpath('cfdi:Emisor', namespaces=namespaces)[0].get('Nombre')
                        rfc_receptor = tree.xpath('cfdi:Receptor', namespaces=namespaces)[0].get('Rfc')
                        name_receptor = tree.xpath('cfdi:Receptor', namespaces=namespaces)[0].get('Nombre')
                        tfd = self._get_stamp_data4(tree)
                        content = etree.tostring(tree, pretty_print=True)
                        xml_file_encode = base64.b64encode(content)

                        cfdi_uuid = tfd.get("UUID")
                        
                        # Búsqueda del UUID en el modelo
                        existing_attachment = attach_obj.sudo().search([
                            ('cfdi_uuid', '=', cfdi_uuid),
                            ('company_id', '=', company_id)
                        ], limit=1)

                        if existing_attachment:
                            # Si el archivo existe, muestra un mensaje y no lo procesa
                            _logger.info("El archivo con UUID %s ya existe. Se omite la creación.", cfdi_uuid)
                            warning_messages.append(_("El archivo con UUID %s ya existe. Se omite la creación.", cfdi_uuid))
    
                        # [ ... LÓGICA DE PROCESAMIENTO RESTANTE ... ]
                        else:
                            # Continúa con la lógica de tu módulo...
                            if tree.get("Folio") != None and tree.get("Serie") != None:
                                ref = str(tree.get("Serie") + str(tree.get("Folio")))
                            elif tree.get("Serie") == None and tree.get("Folio") != None:
                                ref = str(tree.get("Folio"))
                            type_in = ''
                            if rfc_emisor == company_vat and tree.get("TipoDeComprobante") == 'I':
                                type_in = 'I' # Genera factura Cliente
                            if rfc_receptor == company_vat and tree.get("TipoDeComprobante") == 'I':
                                type_in = 'SI' #genera factura provedor
                            if rfc_emisor == company_vat and tree.get("TipoDeComprobante") == 'E':
                                type_in = 'E' # Genera una nota de credito al cliente
                            if rfc_receptor == company_vat and tree.get("TipoDeComprobante") == 'E':
                                type_in = 'SE' # Genera una nota de credito al provedor
                            if tree.get("TipoDeComprobante") == 'P':
                                type_in = 'SP'
                            
                            vals = {
                                'cfdi_type': type_in,
                                'cfdi_uuid': tfd.get("UUID"),
                                'rfc_tercero' : rfc_emisor,
                                'nombre_tercero': name_emisor,
                                'cfdi_total' : tree.get("Total"),
                                'date_cfdi': tree.get('Fecha'),
                                'serie_folio': str(tree.get("Folio")),
                                'name': str(tfd.get("UUID")) + '.xml',
                                'store_fname': str(tfd.get("UUID")) + '.xml',
                                'datas': xml_file_encode,
                                'type' :'binary',
                                'company_id' :company_id,
                            }
                            attach_rec = attach_obj.sudo().create(vals)

                    # Mostrar advertencias sin romper la transacción
                    if warning_messages:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Se completó con advertencias'),
                                'message': '\n'.join(warning_messages),
                                'sticky': True,          # para que el usuario pueda leerlo
                                'type': 'warning',       # info | warning | danger
                                'next': {'type': 'ir.actions.act_window_close'},
                            }
                        }

                    return {'type': 'ir.actions.act_window_close'}
    @api.model
    def _get_stamp_data4(self, cfdi):
        self.ensure_one()
        complemento = cfdi.xpath("//cfdi:Complemento", namespaces={'cfdi': 'http://www.sat.gob.mx/cfd/4'})
        if not complemento:#hasattr(cfdi, 'Complemento'):
            return None
        attribute = '//tfd:TimbreFiscalDigital'
        namespace = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        node = complemento[0].xpath(attribute, namespaces=namespace)
        return node[0] if node else None