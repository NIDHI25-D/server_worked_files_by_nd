from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    abc_classification = fields.Selection([('A', 'High Sales (A)'),
                                           ('B', 'Medium Sales (B)'),
                                           ('C', 'Low Sales (C)')], "ABC Classification")
