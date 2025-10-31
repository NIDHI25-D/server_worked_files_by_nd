from odoo import fields, models, api


class SaleReport(models.Model):
    _inherit = 'sale.report'

    # Customer tags field for sale report filter
    customers_tag_id = fields.Many2many('res.partner.category', column1='partner_id',
                                        column2='category_id', string='Customer Tags',
                                        compute='_compute_customer_tag_id', search='_customer_tag_ids')

    @api.depends('customers_tag_id')
    def _compute_customer_tag_id(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: set Customer Tags from partner.
        """
        self.customers_tag_id = self.partner_id.category_id

    def _customer_tag_ids(self, operator, value):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: added Customer Tags in search view as it is non store field.
        """
        order_id = self.env['sale.order'].search([('partner_id.category_id', operator, value)], limit=None)
        return [('order_id', 'in', order_id.ids)]
