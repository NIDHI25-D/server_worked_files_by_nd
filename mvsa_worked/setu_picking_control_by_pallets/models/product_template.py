from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    package_type = fields.Boolean(string='Package type',default=False)