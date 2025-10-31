from odoo import models


class AccountEdiDocument(models.Model):
    _inherit = 'l10n_mx_edi.document'

    def write(self,vals):
        """
              Author: kishan@setuconsulting.com
              Date: 01/05/2025
              Task: Migration from V16 to V18 (https://app.clickup.com/t/86dtvztcu)
              Purpose: auto send email while signing bank statement journal entry.
        """
        res =  super().write(vals)
        for doc in self:
            if doc.state in ('payment_sent','payment_sent_pue') and doc.move_id and doc.move_id.move_type == 'entry':
                if doc.move_id.statement_line_id:
                    doc.move_id.payment_with_journal_mail_sent()
        return res
