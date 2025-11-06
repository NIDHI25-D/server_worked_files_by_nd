from odoo import _, api, fields, models
from odoo.osv import expression
import ast


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.rule'

    sale_domain = fields.Char(default="[]")

    def _get_valid_sale_domain(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: prepare domain for sale order.
        """
        self.ensure_one()
        domain = []
        if self.sale_domain and self.sale_domain != '[]':
            domain = expression.AND([domain, ast.literal_eval(self.sale_domain)])
        return domain
