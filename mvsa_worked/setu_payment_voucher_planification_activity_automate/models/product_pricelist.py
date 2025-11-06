# -*- coding: utf-8 -*-
from odoo import models, fields, _


class PriceList(models.Model):
    _inherit = "product.pricelist"

    send_mail_activity = fields.Boolean(
        string="Send Mail Activity ?",
        default=False
    )
    send_mail_activity_msg = fields.Char(
        string="Send Mail Activity Message"
    )