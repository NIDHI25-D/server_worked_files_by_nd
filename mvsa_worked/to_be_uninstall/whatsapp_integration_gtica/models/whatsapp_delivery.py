# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class SendWhatsappStock(models.TransientModel):
    _name = 'send.whatsapp.stock'
    _description = 'Send Whatsapp'

    partner_id = fields.Many2one('res.partner', domain="[('parent_id','=',partner_id)]")
    default_messege_id = fields.Many2one('whatsapp.template', domain="[('category', '=', 'delivery')]")

    name = fields.Char(related='partner_id.name')
    mobile = fields.Char(related='partner_id.mobile', help="use country mobile code without the + sign")
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
            Date: 10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is called when format of message is change in delivery
        """
        if self.format_message == 'txt' or self.env.context.get('format_invisible'):
            self.message = self.env.context.get('message_txt', False)
        if self.format_message == 'link':
            self.message = self.env.context.get('message_link', False)

    @api.onchange('default_messege_id')
    def _onchange_message(self):
        stock_picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
        message = self.default_messege_id.template_messege
        incluid_name = ''
        try:
            incluid_name = str(message).format(
                name=stock_picking_id.partner_id.name,
                sales_person=stock_picking_id.user_id.name,
                company=stock_picking_id.company_id.name,
                website=stock_picking_id.company_id.website)
        except Exception:
            raise ValidationError(
                'Quick replies: parameter not allowed in this template, {link_preview} {item_product}')

        if message:
            self.message = incluid_name

    @api.model
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    def sending_reset(self):
        """
            Authour: nidhi@setconsulting
            Date: 10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is for reset button,it will reset the data and close the dialog once message is reset
        """
        stock_picking_id = self.env['stock.picking'].browse(self._context.get('active_id'))
        stock_picking_id.update({
            'send_whatsapp': 'without_sending',
            })
        self.close_dialog()

    @api.model
    def send_dialog(self, whatsapp_url):
        action = {'type': 'ir.actions.act_url', 'url': whatsapp_url, 'target': 'new', 'res_id': self.id}


    def sending_confirmed(self):
        """
            Authour: nidhi@setconsulting
            Date: 08/02/23
            Task: Migration from v14 to v16
            Purpose: This method is used to send message in chatter and close dialog, the kind of message send to user
                     will be reflected in chatter.
        """
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            self.env['whatsapp.mixin'].sending_confirmed(self.message)
            self.close_dialog()

    def sending_error(self):
        """
            Authour: nidhi@setconsulting
            Date: 10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to update the state = no_sent, if message is not send to the user
        """
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            self.env['whatsapp.mixin'].sending_error()
            self.close_dialog()

    def send_whatsapp(self):
        """
            Authour: nidhi@setconsulting
            Date: 08/02/23
            Task: Migration from v14 to v16
            Purpose: This method is used to send the message when "SEND" button is clicked. It will check message,
                     broadcast or mobile.It will open web.whatsapp and send the message to particular mobile
        """
        validation = self.env['whatsapp.mixin'].send_validation_broadcast(self.mobile, self.message, False)

        if validation:
            whatsapp_url = self.env['whatsapp.mixin'].send_whatsapp(self.mobile, self.message, False)

            return {'type': 'ir.actions.act_url',
                    'url': whatsapp_url,
                    'name': "whatsapp_action",
                    'target': 'new',
                    }
