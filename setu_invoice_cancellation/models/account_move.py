from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_cancel_reason_id = fields.Many2one('setu.invoice.cancel', string="Cancellation motive", copy=False)

    # def button_cancel_posted_moves(self):
    #     if self.invoice_cancel_reason_id:
    #         return super(AccountMove, self).button_cancel_posted_moves()
    #     else:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': _('Cancel Reason'),
    #             'res_model': 'out.refund.cancellation',
    #             'view_mode': "form",
    #             'view_id': self.env.ref('setu_invoice_cancellation.request_edi_cancel_view_form').id,
    #             'target': 'new',
    #         }
