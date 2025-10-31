# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_gift_card_line = fields.Boolean(copy=False, default=False)
    shopify_line_id = fields.Char(string="Shopify Line", copy=False)
