import datetime

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.move'

#do this thing in validate instead of create because of {https://app.clickup.com/t/86du98m6b} this task.

    # @api.model
    # def create(self, vals):
    #     """
    #         Author: smith@setuconsulting
    #         Date: 05/05/23
    #         Task: Migraton
    #         Purpose: this method is considered for calculating field
    #                  (1) date_done_date_invoice_diff (Invoicing Duration) is calculated time duration between picking done date and invoice create date.
    #     """
    #     res = super(AccountInvoice, self).create(vals)
    #     resource_obj = self.env['resource.calendar'].sudo()
    #     for invoice in res:
    #         if invoice.move_type == 'out_invoice' and invoice.amount_total > 0:
    #             order = list(set(invoice.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')))
    #             order = order and order[0] or False
    #             if not order:
    #                 order = self.env['sale.order'].sudo().search([('name', '=like', invoice.invoice_origin), ('company_id', '=', invoice.company_id.id)])
    #                 order = order and order[0] or False
    #             # order = order and order[0] or False
    #             if order:
    #                 pickings = order.picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.state == 'done')
    #                 new_transfer = pickings.filtered(lambda x: not x.is_cancellation_invoice)
    #                 if new_transfer:
    #                     for picking in pickings:
    #                         values_to_update = {}
    #                         # if not picking.is_cancellation_invoice:
    #                         date_done_date_invoice_diff = resource_obj.get_shift_wise_hours(picking.date_done, invoice.create_date)
    #                         values_to_update.update({'date_done_date_invoice_diff': date_done_date_invoice_diff})
    #                         invoice.invoice_line_ids.sale_line_ids.order_id.write({'invoice_ref_id': invoice.id})
    #                         if values_to_update:
    #                             picking.write(values_to_update)
    #     return res

    def action_post(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/12/24
            Task: Migration to v18 from v16
            Purpose: calculate date_done_date_invoice_diff from resource calender if transfer is new(cancellation invoice is not checked) during post invoice.
        """
        res = super(AccountInvoice, self).action_post()
        resource_obj = self.env['resource.calendar'].sudo()
        for invoice in self:
            if invoice.move_type == 'out_invoice' and invoice.amount_total > 0:
                order = list(set(invoice.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')))
                order = order and order[0] or False
                if not order:
                    order = self.env['sale.order'].sudo().search([('name', '=like', invoice.invoice_origin), ('company_id', '=', invoice.company_id.id)])
                    order = order and order[0] or False
                if order:
                    pickings = order.picking_ids.filtered(
                        lambda x: x.picking_type_id.code == 'outgoing' and x.state == 'done')
                    new_transfer = pickings.filtered(lambda x: not x.is_cancellation_invoice)
                    if new_transfer:
                        order.write({'invoice_ref_id': invoice.id})
                        for picking in pickings:
                            values_to_update = {}
                            date_done_date_invoice_diff = resource_obj.get_shift_wise_hours(picking.date_done, invoice.create_date)
                            values_to_update.update({'date_done_date_invoice_diff': date_done_date_invoice_diff})
                            if values_to_update:
                                picking.write(values_to_update)
        return res

    def button_cancel_posted_moves(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/12/24
            Task: Migration to v18 from v16
            Purpose: write is_cancellation_invoice field in transfer when invoice are cancel from posted.
        """
        before_status = self.state
        res = super(AccountInvoice, self).button_cancel_posted_moves()
        if res and res.get('type'):
            return res
        if before_status != 'draft' and self.move_type == 'out_invoice':
            picking_ids = self.invoice_line_ids.picking_ids
            for picking_id in picking_ids:
                if not picking_id.is_cancellation_invoice:
                    picking_id.write({'is_cancellation_invoice': True})

