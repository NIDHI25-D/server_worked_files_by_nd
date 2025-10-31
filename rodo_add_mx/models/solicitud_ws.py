# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import base64
import io

import subprocess
import tempfile
import time
import zipfile
# import datetime
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from functools import partial
from lxml import etree, objectify
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from .sat_api_import import SAT
from .special_dict import CaselessDictionary
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from time import sleep
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .portal_sat import PortalSAT

import logging
_logger = logging.getLogger(__name__)


class SolicitudWS(models.Model):
    _name = 'solicitud.ws'
    _description = 'SolicitudWS'
    _rec_name = 'id_solicitud'
    _inherit = ['portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin']

    id_solicitud = fields.Char("ID Solicitud")
    cod_estatus = fields.Char("Codigo Estatus Solicitud")
    mensaje = fields.Char("Estado de solicitud")
    rfc_receptor = fields.Boolean('Solicitud de recibidos', default=False)
    rfc_emisor = fields.Boolean('Solicitud de emitidos', default=False)
    fecha = fields.Date('Fecha de solicitud')
    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    state = fields.Selection([('draft', 'En espera'), ('done', 'Hecho'), ('cancel', 'Error')], string='Estado', default='draft')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    cod_verifica = fields.Char("Codigo Verificacion")
    estado_solicitud = fields.Char("Estado Verificacion")
    mensaje_ver = fields.Char("Mensaje de verificacion")



    content_zip = fields.Binary(
        string='ZIP',
    )
    content_zip_name = fields.Char()

    ir_attachment_count = fields.Integer(compute='_compute_ir_attachment_count', string='# de adjuntos')


    state_zip = fields.Selection([
        ('done', ''),
        ('blocked', '')], string='Estado zip',
        copy=False, default='done', compute='_compute_state_zip')
    
    @api.depends('content_zip_name')
    def _compute_state_zip(self):
        for rec in self:
            if rec.content_zip:
                print("+++++++", len(str(rec.content_zip)), rec.id_solicitud)
                if len(str(rec.content_zip)) > 0:
                    rec.state_zip = 'done'
                else:
                    rec.state_zip = 'blocked'
            else:
                rec.state_zip = 'blocked'
                
    
    def _compute_ir_attachment_count(self):
        for rec in self:
            print("+++  _compute_ir_attachment_count    ++++", self.env['ir.attachment'].search_count([('solicitud_ws_id', '=', rec.id)]))
            rec.ir_attachment_count = self.env['ir.attachment'].search_count([('solicitud_ws_id', '=', rec.id)])


    def action_view_ir_attachment(self):
        for rec in self:
            attachment = self.env['ir.attachment'].search([('solicitud_ws_id', '=', rec.id)])
            ids = []
            if attachment:
                for s in attachment:
                    ids.append(s.id)
            print("ids",ids)
            view_id = self.env.ref('rodo_add_mx.view_attachment_tree_cfdi_sat_invoices_files').id
            f_view = self.env.ref('base.view_attachment_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Documentos digitales',
                'view_mode': 'tree,form',
                'res_model': 'ir.attachment',
                'domain': [('id', 'in', ids)],
                'views': [(view_id, 'tree'),(f_view, 'form')]
            }
        

    


    def get_descomprimir(self):
        for rec in self:
            print("+++  get_descomprimir    +", rec.id)
            attachment_obj = self.env['ir.attachment']

            if rec.content_zip:
                data = base64.b64decode(rec.content_zip)
                zip_ref = zipfile.ZipFile(io.BytesIO(data))
                xml_filenames = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                if xml_filenames:
                    for x in xml_filenames:
                        print("x",x)
                        xml_file = zip_ref.read(x)
                        tree = etree.fromstring(xml_file)
                        content = etree.tostring(tree, pretty_print=True)
                        xml_file_encode = base64.b64encode(content)
                        # print("++   109     ++",xml_file)
                        # print("++   110     ++",tree)
                        print("++   111     ++",content)
                        # print("++   112     ++",xml_file_encode)
                        print("++   113     ++",tree.get("Folio"))
                        print("++   114     ++",tree.get("TipoDeComprobante"))
                        print("++   115     ++",tree.get("Total"))
                        try:
                            ns = tree.nsmap
                            ns.update({'re': 'http://exslt.org/regular-expressions'})
                        except Exception:
                            ns = {'re': 'http://exslt.org/regular-expressions'}
                    
                        try:
                            receptor_elements = tree.xpath("//*[re:test(local-name(), 'Emisor','i')]", namespaces=ns)
                        except Exception:
                            receptor_elements=False
                            _logger.info("No encontró al emisor")
                        r_rfc, r_name, r_folio = '', '',''
                        if receptor_elements:
                            attrib_dict = CaselessDictionary(dict(receptor_elements[0].attrib))
                            r_rfc = attrib_dict.get('rfc') #receptor_elements[0].get(attrib_dict.get('rfc'))
                            r_name = attrib_dict.get('nombre') #receptor_elements[0].get(attrib_dict.get('nombre'))

                        
                        print("++   115     ++",r_rfc)
                        
                        print("++   115     ++",r_name)    
                        cfdi_type = tree.get("TipoDeComprobante",'I')
                        if cfdi_type not in ['I','E','P','N','T']:
                            cfdi_type = 'I'
                        cfdi_type ='S'+cfdi_type

                        name = x.split('.')
                        print("++FECHA++", tree.get('Fecha')[:10])
                        # date = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(tree.get('Fecha'))))[:10]
                        # print(date)

                        vals = dict(
                            name=x,
                            store_fname=x,
                            type='binary',
                            datas=xml_file_encode,
                            cfdi_uuid=name[0],
                            company_id=rec.company_id.id,
                            cfdi_type=cfdi_type,
                            rfc_tercero=r_rfc,
                            nombre_tercero=r_name,
                            serie_folio=tree.get("Folio"),
                            cfdi_total=tree.get("Total"),
                            solicitud_ws_id=rec.id,
                            date_cfdi=tree.get('Fecha')[:10],
                        )

                        print("++++++++",vals)
                        attachment_obj.create(vals)

                rec.state = 'done'


    def get_descargar(self):
        for rec in self:
            print("++   get_descargar   +++", rec.id_solicitud)
            if rec.company_id.synchronize:
                headers = {
                    'Authorization': rec.company_id.token.replace('(', '').replace(')', '').replace("'", '').replace(",", ''),
                    'Content-Type': 'application/json',
                }

                json_data = {
                    'type': 'download',
                    'id_solicitud': rec.id_solicitud,
                }


                #--- PRUEBAS    ---#
                #response = requests.post('http://localhost:8013/api/download', headers=headers, json=json_data)
                #--- -------    ---#

                #--- PRODUCCION    ---#
                response = requests.post('https://tuodoomexico.com/api/download', headers=headers, json=json_data)
                #--- -------    ---#


                if response.status_code == 200:
                    print("+++++", response.json()['result']['ok'])
                    if response.json()['result']['ok'] == True:
                        rec.cod_verifica = response.json()['result']['data']['status_request']                        
                        rec.mensaje_ver = response.json()['result']['data']['msj_request']
                        if response.json()['result']['data']['archivoBase64']:
                            archivoBase64 = response.json()['result']['data']['archivoBase64']
                            archivoBase64 = archivoBase64.encode('utf-8')
                            rec.content_zip = archivoBase64
                            rec.content_zip_name = str(rec.id_solicitud)+str('.zip')
                            rec.get_descomprimir()
                            rec.state = 'done'
                        else:
                            rec.state = 'draft'
                            self.message_post(body=_("Solicitud verificada, aun sin paquete disponible"))
                    else:
                        rec.state = 'draft'
                        self.message_post(body=_("Solicitud verificada, aun sin paquete disponible"))



            