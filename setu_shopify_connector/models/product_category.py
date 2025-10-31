# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_shopify_product_category = fields.Boolean(string="Is Shopify Product Category", default=False)
