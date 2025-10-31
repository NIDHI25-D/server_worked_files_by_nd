from odoo import models


class AccountEdiDocument(models.Model):
    _inherit = 'l10n_mx_edi.document'

    def resign_document(self):
        """
            Author: harshit@setuconsulting.com
            Date: 16/04/25
            Task: Cancel invoice - issue
            Purpose: Cron method for specific 798 code error resign the invoice.
        """
        inv_obj = self.search([('state', 'in', ['invoice_sent_failed','invoice_cancel_failed','invoice_cancel_requested_failed']), ('message', 'not in', [False, ''])])
        moves = []
        for code in inv_obj:
            if '798' in code.message:
                if code.move_id.move_type == 'out_invoice':
                    moves.append(code.move_id)
        # result = moves
        for move in moves:
            if move.l10n_mx_edi_document_ids.filtered(lambda x:not x.attachment_id and x.move_id.move_type == 'out_invoice'):
                move.action_process_edi_web_services(with_commit=False)


    def write(self,vals):
        res = super().write(vals)
        for doc in self:
            if doc.state in('payment_sent','payment_sent_pue') and doc.move_id and doc.move_id.move_type == 'entry' and doc.move_id.payment_ids:
                doc.move_id.payment_ids.mail_sent()
        return res