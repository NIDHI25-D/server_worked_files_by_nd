from odoo import models, fields, api, _
import logging

_logger = logging.getLogger("calculate_values_for_product_levels")


class ProductPriceLevel(models.Model):
    _name = 'product.price.level'
    _description = 'Product Price level based on level configuration'

    competition_level_product = fields.Integer(string="Competition Level", default=False,
                                               compute="_compute_price_level")
    Vendor_id = fields.Many2one("res.partner", compute="_compute_price_level")
    product_id = fields.Many2one("product.product")
    cost_price = fields.Float(string="FOB Cost", compute="_compute_price_level")
    Price = fields.Float(string="Current Price", compute="_compute_price", inverse='_inverse_discount', store=True)
    utility_margin = fields.Float(string="New Margin", compute="_compute_price_level")
    marvel_price = fields.Float("New Price")
    difference = fields.Float("Difference", compute="_compute_increment")
    increment = fields.Float("Increment", compute="_compute_increment")
    marvel_cost = fields.Float("New Cost", compute="_compute_price_level")
    utility = fields.Float(string="Profit Margin", compute="_compute_increment")
    config_id = fields.Many2one("price.level.config", "Related Configuration")
    level_of_config = fields.Integer(related="config_id.level_id.level")
    previous_Price = fields.Float("Previous Price")

    @api.depends('product_id')
    def _compute_price(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used assign the price of list price
        """
        for level in self:
            level.Price = level.product_id.list_price

    def _inverse_discount(self):
        pass

    @api.onchange('marvel_price')
    def _compute_increment(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used calculate the increament,difference,utility
        """
        _logger.debug("Compute _compute_increment method start")
        for level in self:
            utility_disc = 0
            if level.marvel_price:
                level.difference = level.marvel_price / level.Price if level.Price else 0
                level.increment = ((level.marvel_price - level.Price) / level.Price) * 100 if level.Price else 0
                for i in level.config_id.discount_ids:
                    if not utility_disc:
                        utility_disc = (level.marvel_price * (1 - (i.discount / 100))) if level.marvel_cost else 0.0
                        # utility_disc = (((level.marvel_price * (1 - (i.discount / 100))) - level.marvel_cost) / level.marvel_cost) * 100 if level.marvel_cost else 0.0
                    else:
                        utility_disc = utility_disc * (1 - (i.discount / 100))
                utility_disc = ((
                                            utility_disc - level.marvel_cost) / level.marvel_cost) * 100 if level.marvel_cost else 0
                level.utility = utility_disc
            else:
                level.difference = 0
                level.increment = 0
                level.utility = 0
        _logger.debug("Compute _compute_increment method end")

    @api.onchange('product_id', 'Vendor_id')
    def _compute_price_level(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method is used to used to calculate only those products whose purchase.line state is in purchase as well as it will set the vendor and cost price as mentioned in POL
        """
        _logger.debug("Compute _compute_price_level method start")
        for level in self:
            try:
                purchase_order_line = self.env['purchase.order.line'].search(
                    [('product_id', '=', level.product_id.id),('order_id.state', '=', 'purchase')])
                if purchase_order_line and len(purchase_order_line) == 1:
                    level.Vendor_id = purchase_order_line.partner_id.id
                    level.cost_price = purchase_order_line.price_unit
                elif len(purchase_order_line) > 1:
                    latest_pol = purchase_order_line.sorted(lambda ol: ol.order_id.date_approve, reverse=True)[0]
                    level.Vendor_id = latest_pol.partner_id.id
                    level.cost_price = latest_pol.price_unit
                elif level.product_id.seller_ids:
                    level.cost_price = level.product_id.seller_ids[-1].price
                    level.Vendor_id = level.product_id.seller_ids[-1].partner_id
                else:
                    level.cost_price = level.product_id.list_price
                    level.Vendor_id = False
                level.marvel_cost = level.cost_price * level.config_id.exchange_rate * level.config_id.import_factor
                level.competition_level_product = level.product_id.competition_level_id.level
                level.utility_margin = level.config_id.level_ids.filtered(
                    lambda l: int(l.name) == level.product_id.competition_level_id.level).level_Percentage

            except Exception as e:
                _logger.exception(f"ERROR while processing : {e}")
        _logger.debug("Compute _compute_price_level method end")
