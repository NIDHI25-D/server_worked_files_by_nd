from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    warehouse_authorization_ids = fields.One2many('warehouse.transaction.authorization', 'warehouse_id')

