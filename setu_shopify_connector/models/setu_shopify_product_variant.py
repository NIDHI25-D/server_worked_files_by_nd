# -*- coding: utf-8 -*-

import json
import logging
import time
from datetime import datetime, timezone

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .. import shopify
from ..shopify.pyactiveresource.connection import ClientError

_logger = logging.getLogger(__name__)


class SetuShopifyProductVariant(models.Model):
    _name = "setu.shopify.product.variant"
    _description = "Shopify Product Product"
    _order = "sequence"

    active = fields.Boolean(string="Active", default=True)
    is_variant_taxable = fields.Boolean(string="Product Taxable?", default=True)
    is_exported_in_shopify = fields.Boolean(string="Synced", default=False)

    name = fields.Char(string="Product Name", translate=True)
    title = fields.Char(string="Title", translate=True)
    default_code = fields.Char(string="SKU")
    shopify_variant_id = fields.Char(string="Variant ID")
    shopify_inventory_item_id = fields.Char(string="Inventory Item ID")

    sequence = fields.Integer(string="Position", default=1)
    product_cost = fields.Float(string="Product Cost")

    shopify_product_create_date = fields.Datetime(string="Shopify Product Create Date")
    shopify_product_last_updated_date = fields.Datetime(string="Shopify Product Last Updated Date")
    shopify_last_stock_sync_date = fields.Datetime(string="Shopify Last Stock Sync Date", readonly=True)

    product_inventory_policy = fields.Selection(
        [("deny", "Customers are not allowed to place orders for the product variant if it's out of stock."),
         ("continue", "Customers are allowed to place orders for the product variant if it's out of stock"), ],
        string="Product Inventory Policy", default="deny")

    product_inventory_management = fields.Selection(
        [("manage_shopify", "Manage via Shopify"), ("dont_manage_shopify", "Dont Manage via Shopify")],
        string="Inventory Manage", default="manage_shopify")

    odoo_product_id = fields.Many2one("product.product", string="Odoo Product")
    setu_shopify_template_id = fields.Many2one("setu.shopify.product.template", string='Shopify Template',
                                               ondelete="cascade")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)

    setu_shopify_image_ids = fields.One2many("setu.shopify.product.image", "setu_shopify_variant_id",
                                             string="Variant Image IDS")
