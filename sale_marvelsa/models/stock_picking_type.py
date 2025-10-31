from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_enable_create_picking = fields.Boolean('Enable create picking')
