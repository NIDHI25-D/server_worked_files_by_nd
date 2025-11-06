from odoo import fields, models, api, _


class L10nMxEdiInvoiceCancel(models.TransientModel):
    _inherit = 'l10n_mx_edi.invoice.cancel'

    reason_id = fields.Many2one(comodel_name='setu.invoice.cancel', string='Cancellation Motive')

    def action_create_replacement_invoice(self):
        current_move_id = self.env['account.move'].browse(self._context.get('active_id'))
        current_move_id.write({'invoice_cancel_reason_id': self.reason_id.id})
        super(L10nMxEdiInvoiceCancel, self).action_create_replacement_invoice()


    def action_cancel_invoice(self):
        super(L10nMxEdiInvoiceCancel, self).action_cancel_invoice()
        current_move_id = self.env['account.move'].browse(self._context.get('active_id'))
        current_move_id.write({'invoice_cancel_reason_id': self.reason_id.id})
