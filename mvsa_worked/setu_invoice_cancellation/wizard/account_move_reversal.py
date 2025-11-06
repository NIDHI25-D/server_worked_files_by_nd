from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    reason_id = fields.Many2one(comodel_name='setu.invoice.cancel', string='Cancellation Reason', required=True, copy=False)

    def refund_moves(self):
        res = super(AccountMoveReversal, self).refund_moves()
        credit_note_id = self.env['account.move'].browse(res.get('res_id'))
        if credit_note_id:
            credit_note_id.invoice_cancel_reason_id = self.reason_id
        return res
