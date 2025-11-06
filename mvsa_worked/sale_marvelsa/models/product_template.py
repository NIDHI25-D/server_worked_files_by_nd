from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_tag_ids = fields.Many2many('product.tag', 'product_tag_product_template_rel', string='Industry')