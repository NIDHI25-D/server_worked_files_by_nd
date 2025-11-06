from odoo import api, fields, models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: set the value of Intial Order Quantity during back order as per product_uom_qty.
        """
        res = super(StockBackorderConfirmation, self).process()
        button_validate_picking_ids = self._context.get('button_validate_picking_ids')
        if button_validate_picking_ids:
            for rec in button_validate_picking_ids:
                picking_to_reduce_initial_demand = self.env['stock.picking'].browse(rec)
                have_back_order = picking_to_reduce_initial_demand.backorder_ids
                if have_back_order:
                    move_ids = picking_to_reduce_initial_demand.move_ids_without_package
                    for move in move_ids:
                        move.intial_order_quantity = move.product_uom_qty
        return res
