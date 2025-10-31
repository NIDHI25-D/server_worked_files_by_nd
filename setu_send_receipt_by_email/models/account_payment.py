# -*- coding: utf-8 -*-
import base64
import datetime

from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError, ValidationError, MissingError
from odoo.tools.misc import format_date, formatLang

from odoo.addons.mail.models.mail_template import MailTemplate


class AccountPayment(models.Model):
    _inherit = "account.payment"

    vendor_payment_receipt = fields.Binary('Attach Document', copy=False)
    receipt_status = fields.Selection(selection=[('not_sent', 'Not Sent'),
                                                 ('sent', 'Sent')], string='Receipt Status', default='not_sent')
    vendor_payment_receipt_name = fields.Text(string="File Name", tracking=True, copy=False)

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            if rec.vendor_payment_receipt and rec.state == 'paid':
                rec.auto_send_vendor_mail()
        return res

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        if vals.get('vendor_payment_receipt', False):
            self.auto_send_vendor_mail()
        return res

    def auto_send_vendor_mail(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 17/04/2025
              Task: Migration from V16 to V18 (https://app.clickup.com/t/86dtvztcu)
              Purpose: auto send mail while attachment is added.
        """
        for rec in self:
            if rec.state == 'paid' and rec.vendor_payment_receipt:
                template_id = rec.env.ref('setu_send_receipt_by_email.vendor_payment_receipt_template')
                if template_id:
                    file_data = base64.b64decode(rec.vendor_payment_receipt).decode('utf-8', errors='ignore')
                    if any(tag in file_data.lower() for tag in ["<!doctype html>", "<html>", "<head>", "<body>"]):
                        new_attachment_vals = {
                            'name': rec.name, 'datas': rec.vendor_payment_receipt, 'type': 'binary',
                            'res_model': 'mail.message', 'mimetype': 'text/html', 'public': True
                        }
                    else:
                        new_attachment_vals = {
                            'name': rec.name, 'datas': rec.vendor_payment_receipt, 'type': 'binary',
                            'res_model': 'mail.message', 'public': True
                        }
                    attachment_for_mail = rec.env['ir.attachment'].create(new_attachment_vals)
                    message_composer = rec.env['mail.compose.message'].with_context(
                        default_use_template=bool(template_id),
                        custom_layout='mail.mail_notification_light',
                        force_email=True,
                        mail_notify_author=False,
                        default_res_ids=rec.ids,
                        default_template_id=template_id and template_id.id or False,
                        default_model='account.payment',
                        update_replyto=True,
                        send_only_record_partner=True,
                    ).create({})
                    message_composer.attachment_ids = [(6, 0, attachment_for_mail.ids)]
                    message_composer.action_send_mail()
                    rec.write({'receipt_status': 'sent'})

    def payment_with_journal_mail_sent(self):
        """
              Author: kishan@setuconsulting.com
              Date: 01/05/2025
              Task: Migration from V16 to V18 (https://app.clickup.com/t/86dtvztcu)
              Purpose: auto send email while signing bank statement journal entry.
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
            message_composer.write({
                'attachment_ids': [(6, 0, [self.attachment_ids.id, message_composer.attachment_ids.id])],
                'partner_ids': [(6, 0, partners)]
            })
            message_composer.action_send_mail()
