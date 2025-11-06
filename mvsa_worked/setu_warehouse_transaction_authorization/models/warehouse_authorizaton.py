from odoo import fields, models


class WarehouseTransactionAuthorization(models.Model):
    _name = 'warehouse.transaction.authorization'
    _description = 'WarehouseTransactionAuthorization'

    user_id = fields.Many2one(comodel_name='res.users', string='Name')
    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse', string='Authorised Warehouse Transfers')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse Name')
    location_ids = fields.Many2many(comodel_name='stock.location', string='Location Name')
