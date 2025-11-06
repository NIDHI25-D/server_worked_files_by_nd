from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    cedis_plan_ids = fields.One2many('cedis.plan', 'warehouse_id')
