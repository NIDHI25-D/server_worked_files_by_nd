from odoo import models, fields, api, _


class RepairLine(models.Model):
    _inherit = 'repair.line'

    # @api.onchange('type')
    # def onchange_operation_type(self):
    #
    #     args = self.repair_id.company_id and [('company_id', '=', self.repair_id.company_id.id), (
    #         'view_location_id', '=', self.repair_id.location_id.location_id.id)] or []
    #     warehouse = self.env['stock.warehouse'].search(args, limit=1)
    #
    #     if not self.type:
    #         self.location_id = False
    #         self.location_dest_id = False
    #     elif self.type == 'add':
    #         self.onchange_product_id()
    #
    #         self.location_id = warehouse.src_location_add_id
    #         self.location_dest_id = warehouse.dest_location_add_id
    #     else:
    #         self.price_unit = 0.0
    #         self.tax_id = False
    #         self.location_id = warehouse.src_location_delete_id
    #         self.location_dest_id = warehouse.dest_location_delete_id
