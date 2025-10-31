from odoo import api, fields, models, tools


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : customizes the mail values for emails sent through a mass mailing campaign, ensuring that the emails are
        correctly configured with the necessary headers and reply-to addresses
        """
        self.ensure_one()
        res = super(MailComposeMessage, self).get_mail_values(res_ids)
        segment = self.mass_mailing_id and self.mass_mailing_id.rfm_segment_id or False
        # use only for allowed models in mass mailing
        if segment and self.composition_mode == 'mass_mail' and \
                (self.mass_mailing_name or self.mass_mailing_id) and \
                self.env['ir.model'].sudo().search([('model', '=', self.model), ('is_mail_thread', '=', True)], limit=1):
            for res_id in res_ids:
                mail_values = res[res_id]
                email_from = mail_values and mail_values.get('email_from')
                if email_from:
                    mail_values.update({
                        'reply_to': self.env['mail.thread']._notify_get_reply_to(default=email_from, records=None)[False],
                        'message_id': tools.generate_tracking_message_id('message-notify')
                    })
        return res
