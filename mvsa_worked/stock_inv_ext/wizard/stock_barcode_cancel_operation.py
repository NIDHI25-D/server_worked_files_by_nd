# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockBarcodeCancelPicking(models.TransientModel):
    _inherit = 'stock_barcode.cancel.operation'

    def action_cancel_operation(self):
        """
            Author: nidhi@setuconsulting
            Date: 19/03/25
            Task: Error cancel picking's to barcode
            Purpose: during the cancel transfer if Cancellation Reason field no filled in transfer then pop up 'wizard.cancel.reason'
            
        """
        res = self.picking_id.action_cancel()
        if isinstance(res, bool):
            return {'type': 'ir.actions.act_window_close', 'infos': {'cancelled': res}}
        else:
            res['context'] = {'cancel_picking_for_wizard':True,'default_picking_id': self.picking_id.id}
            return res
