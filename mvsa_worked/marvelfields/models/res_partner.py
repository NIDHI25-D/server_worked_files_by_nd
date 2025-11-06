# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.addons.web.controllers.export import ExcelExport
from odoo.exceptions import ValidationError
import base64
import json

FONT_TITLE_LEFT = {'bold': True, 'align': 'left', 'font_color': 'red', 'bg_color': '#fff2cc'}

class ResPartner(models.Model):
    _inherit = "res.partner"

    clasificaciones_ids = fields.Many2many('marvelfields.clasificaciones', 'marvelfields_clasificaciones_rel', 'src_id',
                                           'dest_id', string='Clasificaciones')
    subclases_ids = fields.Many2many('marvelfields.subclases', 'marvelfields_subclases_rel', 'src_id', 'dest_id',
                                     string='Subclases')
    ncliente = fields.Char(string='Numero de Cliente', size=18)
    warehouse_sugerido_id = fields.Many2one('stock.warehouse', string="Surtido Sugerido",
                                            help="Almacen sugerido del cual se ba a surtir el pedido del cliente")
    rutav = fields.Char(string='Ruta')
    payment_days_ids = fields.Many2many('payment.days', 'res_partner_paymnet_days_rel', 'res_partner_id',
                                        'payment_days_id', string="Payment Days")
    collection_executive_id = fields.Many2one("res.users", string="Collection executive")
    zone_id = fields.Many2one('res.partner.zone', string="Zone")
    freight_cost = fields.Monetary('Freight Cost', currency_field='property_purchase_currency_id')
    send_mail_child = fields.Boolean(string="Send Mail")
    send_product_data_update_template = fields.Boolean("Send product data update template", default=False)
    data_to_export = fields.Binary("Data to export")
    billing_general_public_id = fields.Many2one('res.partner', string="Billing General Public")

    bonus_type = fields.Selection(selection=[('credit_note', 'Credit Note'), ('marvelsa_wallet', 'Marvelsa Wallet')],
                                  default='credit_note')

    def send_product_information(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18 (Send Product information to vendor { https://app.clickup.com/t/86drw0y0f })
            Purpose: Send Product information to vendor
        """
        id_send_mail_to = self.env['ir.config_parameter'].sudo().get_param('marvelfields.send_mail_to_id') or False
        if not id_send_mail_to:
            raise ValidationError(_("Please mention user in 'Mail for Product Information' of Settings"))
        partner_ids = self.env['res.partner'].search([('send_product_data_update_template', '=', True)])
        for partner in partner_ids:
            e = ExcelExport()
            product_ids = self.env['product.template'].search([('seller_ids.partner_id', '=', partner.id)])
            data = {"import_compat": False, "domain": [],
                    "fields": [{"name": "id", "label": "ID externo", "type": "integer"},
                               {"name": "default_code", "label": "Referencia interna", "type": "char"},
                               {"name": "name", "label": "Nombre", "type": "char"},
                               {"name": "seller_ids/id", "label": "Vendors/ID externo"},
                               {"name": "seller_ids/display_name", "label": "Vendors", "type": "char"},
                               {"name": "seller_ids/price", "label": "Vendors/Precio", "type": "float"},
                               {"name": "seller_ids/currency_id/full_name", "label": "Vendors/Moneda", "type": "char"},
                               {"name": "seller_ids/min_qty", "label": "Vendors/Cantidad", "type": "float"},
                               {"name": "weight", "label": "Peso", "type": "float"},
                               {"name": "length", "label": "Largo", "type": "float"},
                               {"name": "volume", "label": "Volumen", "type": "float"},
                               {"name": "whidth", "label": "Ancho", "type": "float"},
                               {"name": "high", "label": "Alto", "type": "float"}], "groupby": [],
                    "ids": product_ids.ids, "model": "product.template"}
            response = e.web_export_xlsx(json.dumps(data))
            file_data = base64.encodebytes(response.data)
            template_id = self.env.ref('marvelfields.email_template_for_product_information')
            template_id.send_mail(self.env['res.users'].browse(int(id_send_mail_to)).partner_id.id, force_send=True,
                                  email_values={'recipient_ids': [partner.id],
                                                'email_from': self.env.company.email,
                                                'attachment_ids': [(0, 0, {'name': 'product_updated_information.xlsx',
                                                                           'datas': file_data,
                                                                           'mimetype': 'application/vnd.ms-excel'}), ]})
