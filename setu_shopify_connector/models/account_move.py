# -*- coding: utf-8 -*-

from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = "account.move"

    is_refund_invoice_in_shopify = fields.Boolean(string="Is Refund Invoice In Shopify", default=False)
    shopify_refund_id = fields.Char(string="Shopify Refund Order ID", copy=False)
