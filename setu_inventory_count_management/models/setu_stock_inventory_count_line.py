# -*- coding: utf-8 -*-
from odoo import fields, models


class StockInvCountLine(models.Model):
    _name = 'setu.stock.inventory.count.line'
    _description = 'Stock Inventory Count Line'

    is_discrepancy_found = fields.Boolean(compute="_compute_is_discrepancy_found", store=True, depends=['counted_qty'],
                                          string="Is Discrepancy Found")
    user_calculation_mistake = fields.Boolean(default=False, string="User Calculation Mistake")
    is_multi_session = fields.Boolean(default=False, string="Is Multi session")
    is_system_generated = fields.Boolean(string="System Generated Line")

    theoretical_qty = fields.Float(string="Theoretical Qty")
    qty_in_stock = fields.Float(string="Quantity In Stock")
    counted_qty = fields.Float(string="Counted Quantity")

    state = fields.Selection([('Pending Review', 'Pending Review'), ('Approve', 'Approve'), ('Reject', 'Reject')],
                             default="Pending Review", string="State")

    unscanned_product_line_id = fields.Many2one('setu.unscanned.product.lines', string="Unscanned Product Line")
    inventory_count_id = fields.Many2one(comodel_name="setu.stock.inventory.count", string="Inventory Count")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location")
    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot")

    session_line_ids = fields.One2many('setu.inventory.count.session.line', 'inventory_count_line_id',
                                       string="Session Lines")

    new_count_lot_ids = fields.Many2many('stock.lot', 'new_count_stock_rel', string='New Count Serial Numbers')
    serial_number_ids = fields.Many2many('stock.lot', 'setu_stock_inventory_count_line_stock_lot_rel',
                                         'setu_stock_inventory_count_line_id', 'stock_lot_id', string='Serial Numbers')
    not_found_serial_number_ids = fields.Many2many('stock.lot', 'not_found_stock_lot_rel', 'count_line_id', 'lot_id',
                                                   string='Not Founded Serial Numbers')

    tracking = fields.Selection(related="product_id.tracking", string="Tracking")

    def change_line_state_to_approve(self):
        self.state = 'Approve'

    def change_line_state_to_reject(self):
        self.state = 'Reject'

    def _compute_is_discrepancy_found(self):
        for line in self:
            line.is_discrepancy_found = False
            if line.product_id.tracking == 'serial':
                quants = self.env['stock.quant'].sudo().search(
                    [('location_id', '=', line.location_id.id),
                     ('quantity', '=', 1),
                     ('product_id', '=', line.product_id.id)])
                if not quants:
                    line.is_discrepancy_found = True
                    continue
                additional_quants = list(set(quants.lot_id.ids) ^ set(line.serial_number_ids.ids))
                if additional_quants:
                    line.is_discrepancy_found = True
            elif line.counted_qty != line.qty_in_stock:
                line.is_discrepancy_found = True
