from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_recovery_mail(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 17/04/2025
              Task: Migration from V16 to V18
              Purpose: sending email form journals.
        """
        self.ensure_one()
        if not self.statement_line_id:
            raise UserError(_("This move has no statement line."))
        form_view_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template_id = self.env.ref('setu_send_receipt_by_email.mail_template_data_journal_entry')
        xml_file = self.env['ir.attachment']
        if self.attachment_ids:
            xml_file = self.attachment_ids.filtered(lambda x: x.name.endswith('.xml'))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': form_view_id,
            'target': 'new',
            'context': {
                'default_res_ids': self.statement_line_id.ids,
                'default_model': 'account.bank.statement.line',
                'default_use_template': bool(template_id.id),
                'default_template_id': template_id.id,
                'website_sale_send_recovery_email': True,
                'active_ids': self.statement_line_id.ids,
                'xml_attachment_ids': xml_file.ids
            },
        }

    def payment_with_journal_mail_sent(self):
        """
            Author: nidhi@setconsulting.com
            Date: 18/08/2025
            Task: Request Cancel Issue {https://app.clickup.com/t/86dxh4kca}
            Purpose: modified in 'attachment_ids' key value to remove singleton error
                """
        template_id = self.env.ref('setu_send_receipt_by_email.mail_template_data_journal_entry')
        if template_id:
            message_composer = self.env['mail.compose.message'].with_context(
                default_use_template=bool(template_id),
                custom_layout='mail.mail_notification_light',
                force_email=True, mail_notify_author=True,
                default_res_ids=[self.statement_line_id.id]
            ).create({
                'template_id': template_id and template_id.id or False,
                'model': 'account.bank.statement.line',
                'composition_mode': 'comment'})
            partners = self.partner_id.child_ids.filtered(
                lambda x: x.type == 'followup').ids if self.partner_id.child_ids else []
            partners.append(self.partner_id.id)
            merge_attachments_with_unique_ids = list(set(self.attachment_ids.ids +  message_composer.attachment_ids.ids))
            message_composer.write({
                'attachment_ids': [(6, 0, merge_attachments_with_unique_ids)],
                'partner_ids': [(6, 0, partners)]
            })
            message_composer.action_send_mail()