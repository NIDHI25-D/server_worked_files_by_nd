from odoo import models, fields, api
import pandas as pd
import numpy as np
from datetime import datetime


class SetuFSNXYZInventoryDashboard(models.Model):
    _name = 'setu.fsn.xyz.inventory.dashboard'
    _description = 'FSN-XYZ Inventory Dashboard'

    @api.model
    def get_fsn_xyz_analysis_data(self, start_dt=None, end_dt=None):
        inventory_analysis_type = stock_movement_type = 'all'
        start_date = start_dt if start_dt else datetime.today().replace(month=1, day=1).date().strftime('%Y-%m-%d')
        end_date = end_dt if end_dt else datetime.today().replace(month=12, day=31).date().strftime('%Y-%m-%d')

        query = """
                    Select * from get_inventory_fsn_xyz_analysis_report('%s','%s','%s','%s','%s','%s', '%s', '%s')
                """ % (set(self.env.companies.ids), {}, {}, {}, start_date, end_date, stock_movement_type, inventory_analysis_type)
        self._cr.execute(query)
        stock_data = self._cr.dictfetchall()

        #Data of all active companies
        all_stock_data = pd.DataFrame(stock_data)

        #create Action for onclick method of all charts
        action_click = self.env['setu.inventory.fsn.xyz.analysis.report'].create({
            'start_date': start_date,
            'end_date': end_date,
            'stock_movement_type': stock_movement_type,
            'inventory_analysis_type': inventory_analysis_type,
        })
        final_action_click = action_click.download_report_in_listview()

        # Data of current selected company
        unclean_current_company_stock_data = all_stock_data[all_stock_data['company_id'].isin([self.env.company.id])]

        current_company_stock_data = unclean_current_company_stock_data.dropna(subset=['product_name'])

        company_product_name = np.unique(current_company_stock_data.product_name.dropna().values).tolist()

        # No. of products of current selected company
        total_product_count = company_product_name.__len__()

        fsn_classification = ['F', 'S', 'N']
        xyz_classification = ['X', 'Y', 'Z']

        #clean the

        # Count the product category by fsn and xyz wise
        categorized_fsn_xyz_products_count = current_company_stock_data.groupby(
            ['fsn_classification', 'xyz_classification']).product_id.groups

        # Define the mapping for variable names
        variable_mapping = {
            ('Fast Moving', 'X'): 0,
            ('Fast Moving', 'Y'): 0,
            ('Fast Moving', 'Z'): 0,
            ('Slow Moving', 'X'): 0,
            ('Slow Moving', 'Y'): 0,
            ('Slow Moving', 'Z'): 0,
            ('Non Moving', 'X'): 0,
            ('Non Moving', 'Y'): 0,
            ('Non Moving', 'Z'): 0
        }

        # fetch product count based on classification
        for key in variable_mapping.keys():
            variable_mapping[key] = categorized_fsn_xyz_products_count.get(key, 0).size if key in categorized_fsn_xyz_products_count else 0

        # fetch only list of count from dict
        product_count = list(variable_mapping.values())

        result = {
            'final_action_click': final_action_click,
            'total_product_count': total_product_count,
            'fx_product_count': product_count[0],
            'fy_product_count': product_count[1],
            'fz_product_count': product_count[2],
            'sx_product_count': product_count[3],
            'sy_product_count': product_count[4],
            'sz_product_count': product_count[5],
            'nx_product_count': product_count[6],
            'ny_product_count': product_count[7],
            'nz_product_count': product_count[8],
            'fsn_classification': fsn_classification,
            'xyz_classification': xyz_classification,
        }

        return result