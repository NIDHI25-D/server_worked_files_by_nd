from odoo import api, fields, models


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    blacklist_product_ids = fields.Many2many("product.product", string="Blacklisted Products",
                                             help="Blacklisted Products will not be eligible to get globally "
                                                  "configured loyalty points (Points per product).")
    blacklist_category_ids = fields.Many2many("product.category", string="Blacklisted Categories",
                                              help="All the products under this Blacklisted Product Categories will "
                                                   "not be eligible to get globally configured loyalty points (Points "
                                                   "per product).")
    blacklist_pos_category_ids = fields.Many2many("pos.category", string="Blacklisted POS Categories",
                                                  help="All the products under this Blacklisted POS Categories will "
                                                       "not be eligible to get globally configured loyalty points ("
                                                       "Points per product).")
    blacklist_partner_ids = fields.Many2many("res.partner", string="Blacklisted Customers",
                                             help="Blacklisted Customers will not be eligible to get any type of "
                                                  "loyalty points.")
