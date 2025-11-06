# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentMethod(models.Model):
    _inherit = "payment.method"

    payment_voucher_warning = fields.Boolean(
        string="Payment Voucher warning",
        default=False
    )