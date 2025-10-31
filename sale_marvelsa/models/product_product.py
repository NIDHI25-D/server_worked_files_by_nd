from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_oversized = fields.Boolean(string="Oversized", default=False)
