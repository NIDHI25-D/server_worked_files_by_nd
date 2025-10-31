from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_product_image_id = fields.Char(string="Main Image ID")
