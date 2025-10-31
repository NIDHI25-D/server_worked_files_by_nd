from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Warehouse(models.Model):
	_inherit = "stock.warehouse"

	alternative_warehouse_ids = fields.One2many('alternative.warehouse', 'warehouse_id',
		string='Alternative Warehouses',
        copy=False,
        help="Alternative Warehouses for to Search Stock by Priority for the sale order")
