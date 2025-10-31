from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    need_to_review_website_order = fields.Boolean(string="Review website order", default=False)

    def remove_from_need_to_review(self):
        """
            Author: smith@setuconsulting
            Date: 31/01/23
            Task: Migration
            Purpose: Change the value of a boolean fields
        """
        for so in self:
            so.sudo().write({'need_to_review_website_order': False})
