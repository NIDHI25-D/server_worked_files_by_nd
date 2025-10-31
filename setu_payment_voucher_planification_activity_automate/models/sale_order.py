# -*- coding: utf-8 -*-
from odoo import models, fields, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_payment_voucher_warning = fields.Boolean(
        string="Is Payment Voucher warning?",
        default=False,
        copy=False
    )
    is_sent_payment_receipt = fields.Boolean(
        string="Sent payment receipt",
        default=False
    )
