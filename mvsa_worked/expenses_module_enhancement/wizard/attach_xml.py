from odoo import fields, models, api, _
from lxml import etree, objectify
import base64
from codecs import BOM_UTF8
from odoo.exceptions import UserError

BOM_UTF8U = BOM_UTF8.decode('UTF-8')


class AttachXml(models.TransientModel):
    _name = 'attach.xml'
    _description = "Attach xml"

    dragndrop = fields.Binary(string="Attach XML")
    key = fields.Char()

    # def action_read_xml(self):
    #     self.create_partner(self.dragndrop, False)
    #     self.check_xml({self.key: self.dragndrop})
    #     return True
    #
    # @api.model
    # def check_xml(self, files):
    #     if not isinstance(files, dict):
    #         raise UserError(_("Something went wrong. The parameter for XML ""files must be a dictionary."))
    #     wrongfiles = {}
    #     invoices = {}
    #     outgoing_docs = {}
    #     for key, xml64 in files.items():
    #         try:
    #             if isinstance(xml64, bytes):
    #                 xml64 = xml64.decode()
    #             xml_str = base64.b64decode(xml64.replace(
    #                 'data:text/xml;base64,', ''))
    #             # Fix the CFDIs emitted by the SAT
    #             xml_str = xml_str.replace(
    #                 b'xmlns:schemaLocation', b'xsi:schemaLocation')
    #             xml = objectify.fromstring(xml_str)
    #         except (AttributeError, SyntaxError) as exce:
    #             wrongfiles.update({key: {
    #                 'xml64': xml64, 'where': 'CheckXML',
    #                 'error': [exce.__class__.__name__, str(exce)]}})
    #             continue
    #         if xml.get('TipoDeComprobante', False) == 'E':
    #             outgoing_docs.update({key: {'xml': xml, 'xml64': xml64}})
    #             continue
    #         if xml.get('TipoDeComprobante', False) != 'I':
    #             wrongfiles.update({key: {'cfdi_type': True, 'xml64': xml64}})
    #             continue
    #
    #     return {'wrongfiles': wrongfiles, 'invoices': invoices}
    #
    # @api.model
    # def create_partner(self, xml64, key):
    #     """ It creates the supplier dictionary, getting data from the XML
    #     Receives an xml decode to read and returns a dictionary with data """
    #     # Default Mexico because only in Mexico are emitted CFDIs
    #     hr_expense = self.env['hr.expense'].browse(self._context.get('active_id'))
    #     try:
    #         if isinstance(xml64, bytes):
    #             xml64 = xml64.decode()
    #         xml_str = base64.b64decode(xml64.replace(
    #             'data:text/xml;base64,', ''))
    #         # Fix the CFDIs emitted by the SAT
    #         xml_str = xml_str.replace(
    #             b'xmlns:schemaLocation', b'xsi:schemaLocation')
    #         xml = objectify.fromstring(xml_str)
    #     except BaseException as exce:
    #         return {
    #             key: False, 'xml64': xml64, 'where': 'CreatePartner',
    #             'error': [exce.__class__.__name__, str(exce)]}
    #
    #     rfc_emitter = xml.Emisor.get('Rfc', False)
    #     name = xml.Emisor.get('Nombre', rfc_emitter)
    #
    #     # check if the partner exist from a previos invoice creation
    #     partner = self.env['res.partner'].search([
    #         '|', ('name', '=', name), ('vat', '=', rfc_emitter), '|',
    #         ('company_id', '=', False),
    #         ('company_id', '=', self.env.user.company_id.id)])
    #     self.ensure_one()
    #     fname = ("%s-MX-Bill-%s.xml" % (
    #         hr_expense.product_id.name, hr_expense.company_id.partner_id.vat or '')).replace('/', '')
    #     data_attach = {
    #         'name': fname,
    #         'datas': base64.encodebytes(
    #             etree.tostring(xml).decode().lstrip(BOM_UTF8U).encode('UTF-8') or ''),
    #         'description': _('XML created from %s.') % hr_expense.name,
    #         'res_model': hr_expense._name,
    #         'res_id': hr_expense.id,
    #     }
    #     attachment = self.env['ir.attachment'].create(data_attach)
    #     hr_expense.message_post(
    #         body=_("The document was successfully uploaded."),
    #         attachment_ids=attachment.ids
    #     )
    #
    #     if partner:
    #         hr_expense.partner_id = partner[0].id
    #         return partner
    #
    #     partner = self.env['res.partner'].sudo().create({
    #         'name': name,
    #         'company_type': 'company',
    #         'vat': rfc_emitter,
    #         'country_id': self.env.ref('base.mx').id,
    #         'supplier_rank': 1,
    #         'customer_rank': 0,
    #         'company_id': self.env.user.company_id.id,
    #     })
    #     hr_expense.partner_id = partner.id
    #     msg = _('This partner was created when invoice %s%s was added from '
    #             'a XML file. Please verify that the datas of partner are '
    #             'correct.') % (xml.get('Serie', ''), xml.get('Folio', ''))
    #     partner.message_post(subject=_('Info'), body=msg)
    #
    #     return partner
