from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_considering_in_real_demand = fields.Boolean(string="Is consider In Real Demand")
