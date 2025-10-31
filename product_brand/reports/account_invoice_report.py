from odoo import fields, models, api
from odoo.tools import SQL, sql

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    product_brand_id = fields.Many2one(
        comodel_name='product.brand',
        string='Brand',
    )

    # Customer tags field for account invoice report filter
    customers_tag_id = fields.Many2many('res.partner.category', column1='partner_id',
                                       column2='category_id', string='Customer Tags',
                                       compute='_compute_customer_tag_id', search='_customer_tag_ids')

    @api.depends('customers_tag_id')
    def _compute_customer_tag_id(self):
        self.customers_tag_id = self.partner_id.category_id

    def _customer_tag_ids(self, operator, value):
        """
           Authour: nidhi@setconsulting.com
           Date: 10/12/24
           Task: Migration from V16 to V18
           Purpose: Search invoice through Customer's Category tag in invoice report view.
        """
        invoice_id = self.env['account.invoice.report'].search([('partner_id.category_id', operator, value)], limit=None)
        return [('id', 'in', invoice_id.ids)]


    def _select(self):
        return SQL(
            """%s,template.product_brand_id as product_brand_id""", super(AccountInvoiceReport,self)._select())

