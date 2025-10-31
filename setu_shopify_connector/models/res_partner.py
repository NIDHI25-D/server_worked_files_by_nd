# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_shopify_customer = fields.Boolean(string="Is Shopify Customer", default=False)
    shopify_customer_id = fields.Char(string="Shopify Customer ID")

