from odoo import fields, models


class ShowPopUp(models.TransientModel):
    _name = 'show.pop.up'
    _description = 'show.pop.up'

    def check_again(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 18/03/25
            Task: Migration to v18 from v16
            Purpose: it will show pop up and checked double time check Availability if check field are true in transfer.
        """
        current_picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
        moves = current_picking_id.move_ids
        if moves:
            moves._action_assign()
