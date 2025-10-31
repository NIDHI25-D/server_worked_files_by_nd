from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    repair_location_id = fields.Many2one('stock.location', 'Default repair location',
                                         domain="[('usage', '=', 'internal'),('location_id','=',view_location_id)]")

    src_location_add_id = fields.Many2one('stock.location', 'Source Location (Add)',
                                          domain="[('location_id','=',view_location_id)]")
    dest_location_add_id = fields.Many2one('stock.location', 'Destination Location (Add)')
    src_location_delete_id = fields.Many2one('stock.location', 'Source Location (Delete)')
    dest_location_delete_id = fields.Many2one('stock.location', 'Destination Location (Delete)')
