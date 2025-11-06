from odoo import fields, models


class SetuShopifyProductTemplate(models.Model):
    _inherit = "setu.shopify.product.template"

    shopify_handle = fields.Char(string="Shopify Handle")