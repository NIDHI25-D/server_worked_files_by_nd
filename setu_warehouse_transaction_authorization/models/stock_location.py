from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    bypass_authorization_for_internal = fields.Boolean(string="Bypass warehouse authorization")
