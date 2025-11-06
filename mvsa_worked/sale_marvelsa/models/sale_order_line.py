from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    check_product_type = fields.Selection(related='product_id.type')
    is_discount_group_applied = fields.Boolean(compute="compute_is_group_applied", default=False)
    is_oversized = fields.Boolean(string='Oversized', readonly=True)

    def compute_is_group_applied(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: if set the group Change discount column then only access.
        """

        for line in self:
            line.is_discount_group_applied = self.env.user.has_group('sale_marvelsa.discount_group')

    @api.onchange('product_id')
    def onchange_product_id_for_oversized(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set is_oversized as per sale_order_line product configuration
        """
        for line in self:
            if line.product_id:
                line.is_oversized = line.product_id.is_oversized

    def _prepare_invoice_line(self, **optional_values):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set is_oversized as per sale_order_line
        """
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'is_oversized': self.is_oversized})
        return res
