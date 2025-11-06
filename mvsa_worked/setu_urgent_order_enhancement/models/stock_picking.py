from odoo import fields, models, api


class StockPickingExt(models.Model):
    _inherit = 'stock.picking'
    _order = "urgent_order desc, create_date desc"

    urgent_order = fields.Boolean(string="Urgent Order")