# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

class SendWhatsappPayment(models.TransientModel):
    _name = 'send.whatsapp.payment'
    _description = 'Send Whatsapp Payment'

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.template',domain="[('category', '=', 'payment')]")

    name = fields.Char(related='partner_id.name',required=True,readonly=True)
    mobile = fields.Char(related='partner_id.mobile',help="use country mobile code without the + sign")
    format_message = fields.Selection([('txt', 'Text Plan'),
                                 ('link', 'Link Url'),
                                  ], string="Format Message")
    message = fields.Text(string="Message")
    format_visible_context = fields.Boolean(default=False)

    @api.model
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.format_visible_context = self.env.context.get('format_invisible', False)
        self.mobile = self.partner_id.mobile

    @api.onchange('format_message')
    def _onchange_type(self):
        """
           Authour: nidhi@setconsulting
           Date:10/5/23
           Task: Migration from v14 to v16
           Purpose: This method appears in execution whenever the format_message of whatsapp is changed
        """
        if self.format_message == 'txt' or self.env.context.get('format_invisible'):
            self.message = self.env.context.get('message_txt', False)
        if self.format_message == 'link':
            self.message = self.env.context.get('message_link', False)

    @api.onchange('default_messege_id')
    def _onchange_message(self):
        """
           Authour: nidhi@setconsulting
           Date:10/5/23
           Task: Migration from v14 to v16
           Purpose: This method appears in execution when the message is changed
        """
        payment_id = self.env['account.payment'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege
        incluid_name = ''
        try:
            incluid_name = str(message).format(
                name=payment_id.partner_id.name,
                sales_person=payment_id.invoice_user_id.name,
                company=payment_id.company_id.name,
                website=payment_id.company_id.website)
        except Exception:
            raise ValidationError(
                'Quick replies: parameter not allowed in this template, {link_preview} {item_product}')


        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def sending_reset(self):
        payment_id = self.env['account.payment'].browse(self._context.get('active_id'))
        payment_id.update({
            'send_whatsapp': 'without_sending',
            })
        self.close_dialog()

    def sending_confirmed(self):
        self.env['whatsapp.mixin'].sending_confirmed(self.message)
        self.close_dialog()

    def sending_error(self):
        self.env['whatsapp.mixin'].sending_error()
        self.close_dialog()

    def send_whatsapp(self):
        """
            Authour: nidhi@setconsulting
            Date:10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to send the message through whatsapp of payment
        """
        whatsapp_url = self.env['whatsapp.mixin'].send_whatsapp(self.mobile, self.message, False)

        return {'type': 'ir.actions.act_url',
                'url': whatsapp_url,
                'name': "whatsapp_action",
                'target': 'new',
                }