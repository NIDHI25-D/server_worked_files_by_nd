from odoo import models, fields




class AccountPayment(models.Model):
    """ Shared class between the two sending wizards.
    See 'account.move.send.batch.wizard' for multiple invoices sending wizard (async)
    and 'account.move.send.wizard' for single invoice sending wizard (sync).
    """
    _inherit = 'account.payment'

    def write(self,vals):
        if vals.get('l10n_mx_edi_cfdi_uuid'):
            self.mail_sent()
        return super().write(vals)

    def mail_sent(self):
        template_id = self.env.ref('account.mail_template_data_payment_receipt')
        if template_id:
            message_composer = self.env['mail.compose.message'].with_context(
                default_use_template=bool(template_id),
                custom_layout='mail.mail_notification_light',
                force_email=True, mail_notify_author=True,
                default_res_ids= self.ids
            ).create({
                'template_id': template_id and template_id.id or False,
                'model': 'account.payment',
                'composition_mode': 'comment'})
            partners = self.partner_id.child_ids.filtered(
                lambda x: x.type == 'followup').ids if self.partner_id.child_ids else []
            partners.append(self.partner_id.id)
            attachment_from_moves = self.move_id.attachment_ids.ids
            attachment_from_message_composer = message_composer.attachment_ids.ids
            merge_attachments_with_unique_ids = list(set(attachment_from_moves + attachment_from_message_composer))
            message_composer.write({
                'attachment_ids':[(6,0, merge_attachments_with_unique_ids)],
                'partner_ids' :[(6, 0, partners)]
            })
            message_composer.action_send_mail()
