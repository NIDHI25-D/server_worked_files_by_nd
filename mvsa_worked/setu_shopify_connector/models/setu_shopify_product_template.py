# -*- coding: utf-8 -*-

import base64
import contextlib
import hashlib
import json
import logging
import time
from datetime import datetime
from datetime import timezone
import pytz
import requests
from odoo import models, fields, api

from .. import shopify
from ..shopify.pyactiveresource.connection import ClientError

_logger = logging.getLogger(__name__)
utc = pytz.utc


class SetuShopifyProductTemplate(models.Model):
    _name = "setu.shopify.product.template"
    _description = "Shopify Product Template"

    active = fields.Boolean(string="Active", default=True)

    name = fields.Char(string="Name", translate=True)

    is_shopify_template_exported_shopify = fields.Boolean(string="Synced", default=False)

    shopify_tmpl_id = fields.Char(string="Template ID")
    shopify_template_suffix = fields.Char(string="Template Suffix", translate=True)

    no_total_product_variants = fields.Integer(string="Total Variants", default=0)
    no_total_product_variants_synced = fields.Integer(string="Total Variants Synced",
                                                      compute="_get_compute_total_variants_synced", store=True)

    shopify_template_create = fields.Datetime(string="Template Create")
    last_time_template_update = fields.Datetime(string="Last Time Template Updated")
    shopify_template_published = fields.Datetime(string="Template Published")

    product_published_defined = fields.Selection(
        [('unpublished', 'Unpublished'), ('published_web', 'Published in Online Store Only'),
         ('published_global', 'Published in Online Store and POS')], default='unpublished', copy=False,
        string="Product Published At?")

    product_description = fields.Html(string="Product Description", translate=True)

    odoo_product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    odoo_product_category_id = fields.Many2one("product.category", string="Product Category")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)

    setu_shopify_product_image_ids = fields.One2many("setu.shopify.product.image", "setu_shopify_template_id")
    setu_shopify_product_variant_ids = fields.One2many("setu.shopify.product.variant", "setu_shopify_template_id",
                                                       string="Product Variants")

    setu_shopify_product_tag_ids = fields.Many2many("setu.shopify.product.tag", "setu_shopify_product_tmpl_tags_rel",
                                                    "product_tmpl_id", "setu_shopify_tag_id", string="Product Tags")

    @api.depends("setu_shopify_product_variant_ids.is_exported_in_shopify",
                 "setu_shopify_product_variant_ids.shopify_variant_id")
    def _get_compute_total_variants_synced(self):
        for setu_shopify_template_id in self:
            product_variant_ids = setu_shopify_template_id.setu_shopify_product_variant_ids.filtered(
                lambda prod_id: prod_id.is_exported_in_shopify and prod_id.shopify_variant_id)
            setu_shopify_template_id.no_total_product_variants_synced = product_variant_ids and len(
                product_variant_ids) or 0