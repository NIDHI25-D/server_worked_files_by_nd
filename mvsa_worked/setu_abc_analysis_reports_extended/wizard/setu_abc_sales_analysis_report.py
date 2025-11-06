from odoo import fields, models, api, _
from datetime import *
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class SetuABCSalesAnalysisReport(models.TransientModel):
    _inherit = 'setu.abc.sales.analysis.report'

    def update_product_classification(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 06/01/25
            Task: Migration to v18 from v16
            Purpose: This button is used to upgrade the classification in product model as per the sale of the product.
        """
        config = self.env['ir.config_parameter'].sudo().get_param('setu_abc_analysis_reports_extended.upgrade_product_classification')
        if config:
            if config == '3_months':
                start_date = date.today() - relativedelta(months=3)
            if config == '6_months':
                start_date = date.today() - relativedelta(months=6)
            if config == 'year':
                start_date = date.today() - relativedelta(years=1)
            end_date = date.today()
            category_ids = company_ids = {}
            if self.product_category_ids:
                categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
                category_ids = set(categories.ids) or {}
            products = self.product_ids and set(self.product_ids.ids) or {}

            if self.company_ids:
                companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
                company_ids = set(companies.ids) or {}
            else:
                company_ids = set(self.env.user.company_ids.ids) or {}

            warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}
            query = """
                        update product_product as u set 
                          abc_classification = u2.analysis_category
                        from (
                            Select product_id,analysis_category from get_abc_sales_analysis_data_company_wise('%s','%s','%s','%s','%s','%s', '%s')
                        ) as u2(product_id,analysis_category)
                        where u2.product_id = u.id; 
                        """ % (
                company_ids, products, category_ids, warehouses, start_date, end_date, 'all')
            print(query)
            self._cr.execute(query)
        else:
            raise ValidationError(_('Kindly Mention Product Upgrade Classification in Settings'))