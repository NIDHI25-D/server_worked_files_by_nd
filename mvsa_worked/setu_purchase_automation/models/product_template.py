from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    additional_taxes_ids = fields.Many2many('account.tax', 'product_additional_taxes_rel', 'prod_id', 'tax_id',
                                            string='Additional Taxes',
                                            domain=[('type_tax_use', '=', 'purchase')])
