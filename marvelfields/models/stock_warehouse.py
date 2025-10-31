from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    sugerido = fields.Char(string='Surtido Sugerido')
