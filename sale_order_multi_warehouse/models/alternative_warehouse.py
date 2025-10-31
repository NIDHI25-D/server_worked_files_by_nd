from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AlternativesWarehouses(models.Model):
	_name = 'alternative.warehouse'
	_order = 'priority'

	warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
	warehouse_to_picking_id = fields.Many2one('stock.warehouse', string="Warehouse")
	priority = fields.Integer(string="Priority")

	@api.constrains('priority')
	def _check_priority(self):
		"""
		    Authour: nidhi@setconsulting
		    Date: 6/12/2024
		    Task: Migration from V16 to V18
		    Purpose: This method is used to check the priority mentioned in the warehouse model's alternative warehouse.
		"""
		for rec in self:
			if rec.priority < 0:
				raise UserError(_('The priority field can not less to 0'))
	
	@api.constrains('warehouse_to_picking_id')
	def _check_warehouse_to_picking_id(self):
		"""
		    Authour: nidhi@setconsulting
		    Date: 6/12/2024
		    Task: Migration from V16 to V18
		    Purpose: If the main warehouse is mentioned in the Alternative warehouse then error is raised.
		"""
		for rec in self:
			if rec.warehouse_to_picking_id == rec.warehouse_id:
				raise UserError(_('The warehouse must be different to ' + rec.warehouse_id.name))
