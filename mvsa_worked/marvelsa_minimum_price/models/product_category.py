from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    minimum_price_option = fields.Selection([
        ('amount', 'Cost + Amount'),
        ('percentage', 'Cost + Percentage')
    ], required=False, default='',
        help="The 'Minimum Price Calculation Option: ' " \
             "Leave blank for no minimum price on this category, " \
             "Select Amount for minimum_price = cost + x amount, " \
             "Select Percentage for minimum_price = cost + x percent." \
        )
    minimum_price_amount = fields.Float(required=False, digits=(16, 4), string='Minimum Price Parameter (Amount)')
    minimum_price_percentage = fields.Float(required=False, digits=(16, 4),
                                            string='Minimum Price Parameter (Percentage 1-100)')
