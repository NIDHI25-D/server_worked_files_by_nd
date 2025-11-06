# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import base64
import datetime
import dateutil
import email
import email.policy
import hashlib
import hmac
import json
import lxml
import logging
import pytz
import re
import time
import threading

from collections import namedtuple
from email.message import EmailMessage
from email import message_from_string
from lxml import etree
from werkzeug import urls
from xmlrpc import client as xmlrpclib
from markupsafe import Markup

from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID, Command
from odoo.exceptions import MissingError, AccessError
from odoo.osv import expression
from odoo.tools import is_html_empty
from odoo.tools.misc import clean_context, split_every

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # Remove code because when cc email added in template or follower added odoo raise duplicate constraint
    # error [unique_mail_message_id_res_partner_id_if_set]
    # def _notify_get_recipients_classify(self, message, recipients_data,
    #                                     model_description, msg_vals=None):
    #     """
    #           Author: jay.garach@setuconsulting.com
    #           Date: 17/04/2025
    #           Task: Migration from V16 to V18 (https://app.clickup.com/t/86dtvztcuc)
    #           Purpose: from the auto send mail for vendor only set the context send_only_record_partner to send
    #             only vendor mail and remove the follower of this payment.
    #     """
    #     rec = super(MailThread, self)._notify_get_recipients_classify(message, recipients_data, model_description,
    #                                                                   msg_vals)
    #     if self.env.context.get('send_only_record_partner', False):
    #         rec = [rec[0]]
    #         partner_id = self.mapped('partner_id.id')
    #         rec[0].update({'recipients': partner_id})
    #     return rec

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        """
            Author: nidhi@setuconsulting
            Date: 05/08/2025
            Task: Hidden fields (https://app.clickup.com/t/86dxcmwup) , (https://app.clickup.com/t/86dtvztcuc)
            Purpose: from the auto send mail for vendor only set the context send_only_record_partner to send
            only vendor mail and remove the follower of this payment.
        """
        recipient_data = super()._notify_get_recipients(message, msg_vals, **kwargs)
        if self.env.context.get('send_only_record_partner', False):
            partner_ids = (
                msg_vals.get("partner_ids", [])
                if msg_vals
                else message.sudo().partner_ids.ids
            )
            valid_ids = set(self.mapped("partner_id").ids)
            if valid_ids:
                partner_ids = list(filter(lambda pid: pid in valid_ids, partner_ids))
            recipient_data = [data for data in recipient_data if data["id"] in partner_ids]
        return recipient_data