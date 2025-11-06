from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_picking_id = fields.Many2one('stock.picking')

    def _action_done(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 05/12/24
            Task: Migration from V16 to V18
            Purpose: This method will set the set picking IDs of outgoing to the move and also remove the
            reference if pickings are return type.
        """
        result = super(StockPicking, self)._action_done()
        for res in self:
            if res.picking_type_code == 'outgoing' and res.sale_id:
                stock_moves = res.move_ids.filtered(lambda x: x.state in 'done')
                for move in stock_moves:
                    move.sale_line_id.update({
                        'stock_picking_ids': [(4, res.id)]
                    })
            if res.picking_type_code == 'incoming' and res.return_picking_id:
                stock_moves = res.move_ids.filtered(lambda x: x.state in 'done')
                return_stock_move = res.return_picking_id.move_ids.filtered(lambda x: x.state in 'done')
                return_move_line_qty = 0
                move_line_qty = 0
                for return_move in return_stock_move:
                    return_move_line_qty += return_move.quantity
                for move in stock_moves:
                    move_line_qty += move.quantity
                    if return_move_line_qty == move_line_qty:
                        move.sale_line_id.update({
                            'stock_picking_ids': [(3, res.return_picking_id.id)]
                        })
                        if move.sale_line_id.invoice_lines:
                            move.sale_line_id.invoice_lines.update({
                                'picking_ids': [(3, res.return_picking_id.id)]
                            })
        return result
