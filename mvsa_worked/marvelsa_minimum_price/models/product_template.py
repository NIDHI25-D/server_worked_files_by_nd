from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    minimum_price = fields.Float(string="Minimum Price", help="The lowest price allowed for this product to be sold",
                                 compute='_compute_minimum_price', compute_sudo=True, store=False, digits=(12, 6),
                                 readonly=True)
    minimum_price_option = fields.Selection([
        ('default', 'Follow Category\'s configuration'),
        ('amount', 'Cost + Amount'),
        ('percentage', 'Cost + Percentage'),
        ('disabled', 'Disable minimum price for this product')
    ], required=True, default='default',
        help="The 'Minimum Price Calculation Option: ' " \
             "Leave blank for for following minimum price configuration on its category, " \
             "Select Amount for minimum_price = cost - x amount, " \
             "Select Percentage for minimum_price = cost - x percent." \
        )
    minimum_price_amount = fields.Float(required=False, digits=(16, 4), string='Minimum Price Parameter (Amount)')
    is_minimum_price = fields.Boolean("Enable Minimum Price", compute='_compute_minimum_price_configuration')
    minimum_price_percentage = fields.Float(required=False, digits=(16, 4),
                                            string='Minimum Price Parameter (Percentage 1-100)')

    @api.depends('is_minimum_price')
    def _compute_minimum_price_configuration(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: This method will check whether the boolean of minimum price is enable or not
        """
        config = self.env['ir.config_parameter'].sudo().get_param('marvelsa_minimum_price.enable_minimum_price')
        if config:
            self.is_minimum_price = True
        else:
            self.is_minimum_price = False

    @api.depends('minimum_price_option', 'minimum_price_amount', 'minimum_price_percentage', 'standard_price',
                 'categ_id', 'categ_id.minimum_price_option', 'categ_id.minimum_price_amount',
                 'categ_id.minimum_price_percentage')
    def _compute_minimum_price(self):
        """
            Author: jay.garach@setuconsulting.com
            Date:  10/12/24
            Task: Migration from V16 to V18
            Purpose: This method will calculate the minimum_price of the product as per the product category.User need to
                     mention the amount/percentage in product_category and as per the selected option it will be calculated
        """
        _logger.debug("Compute _compute_minimum_price method start")
        for product in self:
            if product.minimum_price_option == 'default':
                # Follow category's setup if default
                categ = product.categ_id
                if categ.minimum_price_option == 'amount':
                    product.minimum_price = product.standard_price + categ.minimum_price_amount
                elif categ.minimum_price_option == "percentage":
                    product.minimum_price = product.standard_price + (
                            product.standard_price * (categ.minimum_price_percentage / 100))
                else:
                    product.minimum_price = 0

            elif product.minimum_price_option == 'amount':
                product.minimum_price = product.standard_price + product.minimum_price_amount
            elif product.minimum_price_option == 'percentage':
                product.minimum_price = product.standard_price + (
                        product.standard_price * (product.minimum_price_percentage / 100))
            else:
                # If blank and disabled should be always pass or 0
                product.minimum_price = 0
        _logger.debug("Compute _compute_minimum_price method end")
