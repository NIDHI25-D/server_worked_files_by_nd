# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProductBrand(models.Model):
    _inherit = "product.brand"

    enable_exclude_products = fields.Boolean(string="Enable Exclude Products")
    country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="product_brand_country_rel",
        column1="product_brand_id",
        column2="country_id",
        string="Countries")
