from odoo import models, fields, api
import pandas as pd
import numpy as np


class SetuXYZInventoryDashboard(models.Model):
    _name = 'setu.xyz.inventory.dashboard'
    _description = 'XYZ Inventory Dashboard'

    @api.model
    def get_xyz_analysis_data(self):
        inventory_analysis_type = 'all'
        query = """
                        Select * from get_inventory_xyz_analysis_data('%s','%s','%s','%s')
                    """ % (set(self.env.companies.ids), {}, {}, inventory_analysis_type)
        self._cr.execute(query)
        stock_data = self._cr.dictfetchall()

        line_action = self.env['setu.inventory.xyz.analysis.report'].create({
            'inventory_analysis_type': 'all',
        })
        final_line_action = line_action.download_report_in_listview()

        # Data of all active companies
        df_all_stock_data = pd.DataFrame(stock_data)

        # Data of current selected company
        df_stock_data = df_all_stock_data[df_all_stock_data['company_id'].isin([self.env.company.id])]

        currency_name = self.env.company.currency_id.symbol
        overall_stock_value = round(sum(df_stock_data.stock_value.values), 2)

        company_total_product_name = np.unique(df_stock_data.product_name.dropna().values).tolist()
        total_product_count = company_total_product_name.__len__()

        # Count the product category wise
        categorized_products_data_count = df_stock_data.groupby(
            ['category_name', 'analysis_category']).product_id.count().reset_index()

        # Fetch data product category and analysis wise
        company_stock_data = df_stock_data.groupby(['category_name', 'analysis_category']).agg(
            {
                'current_stock': 'sum',
                'stock_value': 'sum'
            }
        ).reset_index()

        # Fetch data company and analysis wise
        all_companies_stock_data = df_all_stock_data.groupby(['company_name', 'analysis_category']).agg(
            {
                'current_stock': 'sum',
                'stock_value': 'sum'
            }
        ).reset_index()

        # group data by analysis category
        analyzed_stock_data = df_stock_data.groupby('analysis_category').agg({
            'current_stock': 'sum',
            'stock_value': 'sum'
        })

        category_name = np.unique(company_stock_data.category_name.dropna().values).tolist()
        product_count_by_category = {key: {'X':0, 'Y':0, 'Z':0} for key in category_name}

        if not analyzed_stock_data.empty:
            x_stock_value = round(analyzed_stock_data.stock_value.X, 2) if 'X' in analyzed_stock_data.stock_value else 0
            y_stock_value = round(analyzed_stock_data.stock_value.Y, 2) if 'Y' in analyzed_stock_data.stock_value else 0
            z_stock_value = round(analyzed_stock_data.stock_value.Z, 2) if 'Z' in analyzed_stock_data.stock_value else 0
        else:
            x_stock_value = y_stock_value = z_stock_value = 0

        x_product_count = y_product_count = z_product_count = 0

        category_product_name = {key: [] for key in category_name}
        for index, row in df_stock_data.iterrows():
            if row['product_name'] in company_total_product_name:
                if 'X' in row['analysis_category']:
                    x_product_count += 1

                elif 'Y' in row['analysis_category']:
                    y_product_count += 1
                elif 'Z' in row['analysis_category']:
                    z_product_count += 1

                if row['category_name'] in category_product_name.keys() and not row['product_name'] in category_product_name[row['category_name']]:
                    category_product_name[row['category_name']].append(row['product_name'])
                    product_count_by_category[row['category_name']][row['analysis_category']] += 1


        # Product Category wise stock and values
        stock_category_data = {}
        for _, row in company_stock_data.iterrows():
            category = row['category_name']
            analysis = row['analysis_category']

            # Add to the dictionary if the category doesn't exist yet
            if category not in stock_category_data:
                stock_category_data[category] = {}

            # Add the analysis_category data (current_stock, stock_value)
            stock_category_data[category][analysis] = {
                'current_stock': row['current_stock'],
                'stock_value': round(row['stock_value'], 2)
            }

        for _, row in categorized_products_data_count.iterrows():
            category = row['category_name']
            analysis = row['analysis_category']

            # Add to the dictionary if the category doesn't exist yet
            if category not in stock_category_data:
                stock_category_data[category] = {}

            # Add the analysis_category data (current_stock, stock_value)
            stock_category_data[category][analysis].update({
                'product_count': row['product_id']
            })

        # company wise stock and values
        stock_company_data = {}
        for _, row in all_companies_stock_data.iterrows():
            company = row['company_name']
            analysis = row['analysis_category']

            # Add to the dictionary if the category doesn't exist yet
            if company not in stock_company_data:
                stock_company_data[company] = {}

            # Add the analysis_category data (current_stock, stock_value)
            stock_company_data[company][analysis] = {
                'current_stock': row['current_stock'],
                'stock_value': row['stock_value']
            }
        else:
            for company in self.env.companies:
                classifications = ['X', 'Y', 'Z']
                if company.name not in stock_company_data:
                    stock_company_data[company.name] = {}
                    for clf in classifications:
                        stock_company_data[company.name][clf] = {'current_stock': 0, 'stock_value': 0}
                else:
                    for cfl in classifications:
                        if cfl not in stock_company_data[company.name]:
                            stock_company_data[company.name][cfl] = {'current_stock': 0, 'stock_value': 0}

        result = {
            'line_action': final_line_action,
            'currency_name': currency_name,
            'total_stock_value': overall_stock_value,
            'total_product_count': total_product_count,
            'x_stock_value': x_stock_value,
            'x_product_count': x_product_count,
            'y_stock_value': y_stock_value,
            'y_product_count': y_product_count,
            'z_stock_value': z_stock_value,
            'z_product_count': z_product_count,
            'category_name': category_name,
            'company_name': list(stock_company_data.keys()),
            'classification': np.unique(company_stock_data.analysis_category.values).tolist(),
            'stock_category_data': stock_category_data,
            'stock_company_data': stock_company_data,
            'current_stock': company_stock_data.current_stock.values.astype(str).tolist(),
            'stock_value': company_stock_data.stock_value.values.astype(str).tolist(),
            'product_count_by_category': product_count_by_category,
        }

        return result
