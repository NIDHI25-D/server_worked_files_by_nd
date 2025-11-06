# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SetuShopifyProductImage(models.Model):
    _name = "setu.shopify.product.image"
    _description = "Shopify Product Image"
    _order = "sequence, create_date desc, id"

    setu_shopify_product_image_id = fields.Char(string="Shopify Product Image ID")

    sequence = fields.Integer(help="Sequence of images.", index=True, default=10)

    setu_generic_product_image_id = fields.Many2one("setu.generic.product.image", string="Generic", ondelete="cascade")
    setu_shopify_variant_id = fields.Many2one("setu.shopify.product.variant", string="Shopify Variant ID")
    setu_shopify_template_id = fields.Many2one("setu.shopify.product.template", string="Shopify Template ID")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',string='Multi e-Commerce Connector')

    image = fields.Image(related="setu_generic_product_image_id.image", string="Variant Image")
    image_url = fields.Char(related="setu_generic_product_image_id.url", string="Image URL")
