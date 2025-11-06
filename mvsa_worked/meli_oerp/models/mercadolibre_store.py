from odoo import api, fields, models


class MercadoLibreStore(models.Model):
    _name = 'mercadolibre.store'
    _description = 'MercadoLibreStore'

    name = fields.Char(string="Store Name")
    store_id = fields.Integer(string="Store id")
    mercadolibre_company_id = fields.Many2one('res.company', string="Mercado Libre Instance")