import logging
import pytz
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
utc = pytz.utc


class SetuOracleProductTemplate(models.Model):
    _name = "setu.oracle.product.template"
    _description = "Oracle Product Template"

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Name", translate=True)
    is_oracle_template_exported_oracle = fields.Boolean(string="Synced", default=False)
    oracle_tmpl_id = fields.Char(string="Template ID")
    oracle_template_suffix = fields.Char(string="Template Suffix", translate=True)
    no_total_product_variants = fields.Integer(string="Total Variants", default=0)
    setu_oracle_product_variant_ids = fields.One2many("setu.oracle.product.variant", "setu_oracle_template_id",
                                                      string="Product Variants")
    synchronizationId = fields.Char('Last synchronizationId')
    oracle_template_create = fields.Datetime(string="Template Create")
    last_time_template_update = fields.Datetime(string="Last Time Template Updated")
    oracle_template_published = fields.Datetime(string="Template Published")
    default_code = fields.Char(string="SKU")
    product_published_defined = fields.Selection(
        [('unpublished', 'Unpublished'), ('published_web', 'Published in Online Store Only')], default='unpublished',
        copy=False, string="Product Published At?")
    product_description = fields.Html(string="Product Description", translate=True)
    product_brand_id = fields.Many2one("product.brand", string="Brand")
    odoo_product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    odoo_product_category_id = fields.Many2one("product.category", string="Product Category")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)

    # def oracle_product_publish_unpublish(self):
    #     pass
