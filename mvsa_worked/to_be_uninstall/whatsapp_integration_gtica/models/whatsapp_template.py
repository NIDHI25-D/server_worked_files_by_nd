# -*- coding: utf-8 -*-

import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class WhatsappTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'Message default in Whatsapp'

    name = fields.Char(string="Title Template")
    template_messege = fields.Text(string="Message Template")
    category = fields.Selection([('partner', 'Partner/Contact'),
                                 ('sale', 'Sale/Quoting'),
                                 ('invoice', 'Invoice'),
                                 ('delivery', 'Delivery/Stock'),
                                 ('lead', 'CRM/Marketing'),
                                 ('purchase', 'Provider'),
                                 ('other', 'Other')], default='other', string="Category")


class WhatsappApiSend(models.AbstractModel):
    _name = "whatsapp.mixin"
    _description = "Send Validation and Send Whatsapp"

    def send_validation_broadcast(self, mobile, message, broadcast):
        """
            Authour: nidhi@setconsulting
            Date:10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to check the condition, whether mobile,message or brodcast is given or not.
                     If message, mobile or broadcast is not available it will give error meassage accordingly
        """
        if not mobile and not message and not broadcast:
            raise ValidationError(
                _("You must add the mobile number or message (You can use the broadcast list option)"))
        if not mobile and message and not broadcast:
            raise ValidationError(_("You must add the mobile number (You can use the broadcast list option)"))
        if (not mobile and not message and broadcast) or (mobile and not message and not broadcast) or (
                mobile and not message and broadcast):
            raise ValidationError(_("You must add the message"))

        return True

    def sending_confirmed(self, message):
        """
            Authour: nidhi@setconsulting
            Date:10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to update the state = sent, if message is send to the user
        """
        active_model = self.env.context.get('active_model')
        active_view = self.env[active_model].browse(self._context.get('active_id'))

        message_fomat = '<p class="text-info">Successful Whatsapp</p><p><b>Message sent:</b></p>%s' % message
        active_view._action_whatsapp_confirmed(message_fomat.replace('\n', '<br>'))
        active_view.update({
            'send_whatsapp': 'sent',
        })

    def sending_error(self):
        """
            Authour: nidhi@setconsulting
            Date:10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to update the state = no_sent, if message is not send to the user
        """
        active_model = self.env.context.get('active_model')
        active_view = self.env[active_model].browse(self._context.get('active_id'))

        message_fomat = '<p class="text-danger">Error Whatsapp</p><p>The recipient may not have whatsapp / verify the country code / other reasons</p>'
        active_view._action_whatsapp_confirmed(message_fomat.replace('\n', '<br>'))
        active_view.update({
            'send_whatsapp': 'not_sent',
        })

    def send_whatsapp(self, mobile, message, broadcast):
        """
            Authour: nidhi@setconsulting
            Date: 10/5/23
            Task: Migration from v14 to v16
            Purpose: This method is used to send the message from whatsapp so whatsapp api is called.Need to log-in
                    to whatsapp id not
        """
        if mobile:
            movil = mobile
            array_int = re.findall("\d+", movil)
            whatsapp_number = ''.join(str(e) for e in array_int)

        if message:
            messege_prepare = u'{}'.format(message)
            messege_encode = urllib.parse.quote(messege_prepare.encode('utf8'))

        mobileRegex = r"android|webos|iphone|ipod|blackberry|iemobile|opera mini"
        user_agent = request.httprequest.environ.get('HTTP_USER_AGENT', '').lower()
        match = re.search(mobileRegex, user_agent)

        if broadcast:
            if match:
                whatsapp_url = 'https://api.whatsapp.com/send?text={}'.format(messege_encode)
            else:
                whatsapp_url = 'https://web.whatsapp.com/send?text={}'.format(messege_encode)
        else:
            if match:
                whatsapp_url = 'https://api.whatsapp.com/send?phone={}&text={}'.format(whatsapp_number, messege_encode)
            else:
                whatsapp_url = 'https://web.whatsapp.com/send?phone={}&text={}'.format(whatsapp_number, messege_encode)

        return whatsapp_url
