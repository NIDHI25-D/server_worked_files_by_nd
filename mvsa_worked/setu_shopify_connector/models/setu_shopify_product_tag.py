# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SetuShopifyProductTag(models.Model):
    _name = "setu.shopify.product.tag"
    _description = "Product Shopify Tag"

    name = fields.Char(string="Name", translate=True)
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector', string='Multi e-Commerce Connector', copy=False)

