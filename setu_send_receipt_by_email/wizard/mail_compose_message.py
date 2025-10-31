from odoo import fields, models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _compute_attachment_ids(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 17/04/2025
              Task: Migration from V16 to V18
              Purpose: if sending mail form journals then attach the CFDI Document.
        """
        res = super(MailComposeMessage, self)._compute_attachment_ids()
        for rec in self:
            if rec._context.get('xml_attachment_ids'):
                xml_files = self.env['ir.attachment'].browse(i for i in rec._context.get('xml_attachment_ids'))
                rec.attachment_ids += xml_files
        return res

    def _action_send_mail_comment(self, res_ids):
        """ Send in comment mode. It calls message_post on model, or the generic
        implementation of it if not available (as message_notify). """
        self.ensure_one()
        template_id = self.env.ref('setu_send_receipt_by_email.mail_template_data_journal_entry')
        if self.model == 'account.bank.statement.line' and self.template_id == template_id:
            messages = self.env['mail.message']
            post_values_all = self._prepare_mail_values(res_ids)
            for res_id, post_values in post_values_all.items():
                move_id = self.env[self.model].browse(self.env.context.get('default_res_ids', [])).move_id
                if move_id:
                    messages += move_id.message_post(**post_values)
            return messages

        messages = super(MailComposeMessage, self)._action_send_mail_comment(res_ids)
        return messages
