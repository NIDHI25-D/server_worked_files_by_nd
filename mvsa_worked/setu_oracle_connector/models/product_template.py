from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # def write(self, vals):
    #     res = super().write(vals)
    #     return res
