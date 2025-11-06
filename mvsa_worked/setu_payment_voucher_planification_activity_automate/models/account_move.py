# -*- coding: utf-8 -*-
from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = "account.move"

    is_sent_payment_receipt_account = fields.Boolean(
        string="Sent payment receipt account",
        default=False,
        copy= False
    )
