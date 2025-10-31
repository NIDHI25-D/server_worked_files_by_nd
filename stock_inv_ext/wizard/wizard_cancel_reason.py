from odoo import api, fields, models


class WizardCancelReason(models.TransientModel):
    _name = 'wizard.cancel.reason'
    _description = 'Wizard to add cancel reason to stock picking'

    order_fill_error_picking_id = fields.Many2one('order.fill.error.picking', string='Cancellation Reason')

    def confirm_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 18/03/25
            Task: Migration to v18 from v16
            Purpose: during the cancel transfer if Cancellation Reason field no filled in transfer then pop up this otherwise called action_cancel.

            Task : Error cancel picking's to barcode [https://app.clickup.com/t/86dx5ee0a]
            modified: in context not getting picking_id from active_id in barcode during picking cancel and [also add 'ir.actions.act_window_close' to display message picking cancel--- odoo functionality]
        """
        picking = self.env['stock.picking'].browse(self.env.context.get('default_picking_id')) or self.env['stock.picking'].browse(self.env.context.get('active_id'))
        picking.order_fill_error_picking_id = self.order_fill_error_picking_id
        res = picking.action_cancel()
        if self.env.context.get('cancel_picking_for_wizard'):
            return {'type': 'ir.actions.act_window_close', 'infos': {'cancelled': res}}
        return res
