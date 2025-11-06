import numpy as np
import pandas as pd

from odoo import fields, models, api, _
from datetime import datetime

class SetuOverstockDashboard(models.Model):
    _name = 'setu.overstock.dashboard'
    _description = 'Setu Overstock Dashboard'

    @api.model
    def return_overstock_analysis(self, start_dt=None, end_dt=None, adv_stock_days = None):
        start_date = start_dt if start_dt else datetime.today().replace(month=1, day=1).date().strftime('%Y-%m-%d')
        end_date = end_dt if end_dt else datetime.today().replace(month=12, day=31).date().strftime('%Y-%m-%d')
        advance_stock_days = adv_stock_days if adv_stock_days else '30'

        company = self.env.company.id
        company_currency_symbol = self.env.company.currency_id.symbol

        query = """
                    Select * from get_products_overstock_data('{%s}','{}','{}','{}','%s','%s', '30')
                """ % (company, start_date, end_date)
        self._cr.execute(query)
        data = self._cr.dictfetchall()

        line_action = self.env['setu.inventory.overstock.report'].create({
            'advance_stock_days': advance_stock_days,
            'start_date': start_date,
            'end_date': end_date
        })

        final_line_action = line_action.download_report_in_listview()

        all_stock_data = pd.DataFrame(data)
        unclean_current_company_stock_data = all_stock_data[all_stock_data['company_id'].isin([self.env.company.id])]
        current_company_stock_data = unclean_current_company_stock_data.dropna(subset=['product_name'])
        company_product_name = np.unique(current_company_stock_data.product_name.dropna().values).tolist()
        total_prod = company_product_name.__len__()

        overstock_product_count = len(set([item.get('product_id') for item in data if item.get('overstock_qty', 0) > 0]))
        overstock_valuation = sum([item.get('overstock_value') for item in data if item.get('overstock_qty', 0) > 0])

        #to add fsn-xyz report in overstock
        overstock_product_ids = [item.get('product_id') for item in data if item.get('overstock_qty', 0) > 0]

        # Initialize dictionaries for overstock quantity grouping
        overall_stock_valuation = 0

        overstock_qty_by_product_category = {}
        overstock_qty_by_warehouse = {}

        # Iterate over records to calculate groupings
        for item in data:
            product_id = self.env['product.product'].browse(item.get('product_id'))
            category_name = item.get('category_name')
            warehouse_name = item.get('warehouse_name')

            # Initialize dictionary keys with a list [count, overstock_value_sum] if not present
            if category_name not in overstock_qty_by_product_category:
                overstock_qty_by_product_category[category_name] = [0, 0]  # [count, overstock_value_sum]
            if warehouse_name not in overstock_qty_by_warehouse:
                overstock_qty_by_warehouse[warehouse_name] = [0, 0]  # [count, overstock_value_sum]

            # Process items with overstock_qty > 0
            if item.get('overstock_qty', 0) > 0:
                # Increment count (first element in the list)
                overstock_qty_by_product_category[category_name][0] += 1
                overstock_qty_by_warehouse[warehouse_name][0] += 1

                # Add to overstock_value_sum (second element in the list)
                overstock_value = item.get('overstock_value', 0)
                overstock_qty_by_product_category[category_name][1] += overstock_value
                overstock_qty_by_warehouse[warehouse_name][1] += overstock_value

            # # Calculate total valuation
            if item.get('qty_available') and product_id.standard_price:
                overall_stock_valuation += item['qty_available'] * product_id.standard_price

        overall_stock_valuation = round(overall_stock_valuation, 2)
        overall_stock_valuation = round(overall_stock_valuation, 2)

        dict = {
            'company_currency_symbol': company_currency_symbol,
            'total_prod': total_prod,
            'overall_stock_valuation': overall_stock_valuation,
            'overstock_product_count': overstock_product_count,
            'overstock_valuation': overstock_valuation,
            'overstock_qty_by_product_category': overstock_qty_by_product_category,
            'overstock_qty_by_warehouse': overstock_qty_by_warehouse,
            'final_line_action': final_line_action
        }


        return dict

