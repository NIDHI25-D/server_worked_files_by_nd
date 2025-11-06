# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    payment_voucher_warning = fields.Boolean(
        string="Payment Voucher warning",
        default=False
    )