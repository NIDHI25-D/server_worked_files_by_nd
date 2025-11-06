from odoo import models, fields, api
import pandas as pd
import numpy as np
from datetime import datetime


class SetuStockMovementInventoryDashboard(models.Model):
    _name = 'setu.stock.movement.inventory.dashboard'
    _description = 'Stock Movement Inventory Dashboard'

    @api.model
    def get_stock_movement_analysis_data(self, start_dt=None, end_dt=None):
        start_date = start_dt if start_dt else datetime.today().replace(month=1, day=1).date().strftime('%Y-%m-%d')
        end_date = end_dt if end_dt else datetime.today().replace(month=12, day=31).date().strftime('%Y-%m-%d')

        query = """
            Select * from get_products_stock_movements('%s','%s','%s','%s','%s','%s')
        """%(set(self.env.companies.ids), {}, {}, {}, start_date, end_date)
        self._cr.execute(query)
        stock_movement_data = self._cr.dictfetchall()

        # Data of all active companies
        all_stock_movement_data = pd.DataFrame(stock_movement_data)

        action_click = self.env['setu.stock.movement.report'].create({
            'start_date': start_date,
            'end_date': end_date
        })
        final_action_click = action_click.download_report_in_listview()

        # Data of current selected company
        unclean_current_company_stock_movement_data = all_stock_movement_data[all_stock_movement_data['company_id'].isin([self.env.company.id])]

        current_company_stock_movement_data = unclean_current_company_stock_movement_data.dropna(subset=['product_name'])

        company_product_name = np.unique(current_company_stock_movement_data.product_name.values).tolist()
        # No. of products of current selected company
        total_product_count = company_product_name.__len__()

        # No. of products that have been sold
        sale_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['sales'] > 0].product_name.values).tolist().__len__()
        # No. of products that have been sold then return
        sale_return_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['sales_return'] > 0].product_name.values).tolist().__len__()
        # No. of products that have been purchased
        purchase_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['purchase'] > 0].product_name.values).tolist().__len__()
        # No. of products that have been purchased then return
        purchase_return_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['purchase_return'] > 0].product_name.values).tolist().__len__()
        # No. of products that have been adjusted In
        adjustment_in_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['adjustment_in'] > 0].product_name.values).tolist().__len__()
        # No. of products that have been adjusted Out
        adjustment_out_total_product = np.unique(current_company_stock_movement_data[current_company_stock_movement_data['adjustment_out'] > 0].product_name.values).tolist().__len__()

        total_warehouse_name = np.unique(current_company_stock_movement_data.warehouse_name.values).tolist()
        warehouse_stock_movement_data = {}
        for warehouse_name in total_warehouse_name:
            warehouse_data = current_company_stock_movement_data[current_company_stock_movement_data['warehouse_name'].isin([warehouse_name])]

            warehouse_stock_movement_data.update({
                warehouse_name: {
                    'Sales': np.unique(
                        list(warehouse_data[warehouse_data['sales'] > 0].groupby('product_name').groups.keys())).size,
                    'Sales Return': np.unique(list(
                        warehouse_data[warehouse_data['sales_return'] > 0].groupby('product_name').groups.keys())).size,
                    'Purchase': np.unique(list(
                        warehouse_data[warehouse_data['purchase'] > 0].groupby('product_name').groups.keys())).size,
                    'Purchase Return': np.unique(list(warehouse_data[warehouse_data['purchase_return'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Transit In': np.unique(list(
                        warehouse_data[warehouse_data['transit_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Transit Out': np.unique(list(
                        warehouse_data[warehouse_data['transit_out'] > 0].groupby('product_name').groups.keys())).size,
                    'Opening Stock': np.unique(list(warehouse_data[warehouse_data['opening_stock'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Closing Stock': np.unique(
                        list(warehouse_data[warehouse_data['closing'] > 0].groupby('product_name').groups.keys())).size,
                    'Adjustment In': np.unique(list(warehouse_data[warehouse_data['adjustment_in'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Adjustment Out': np.unique(list(warehouse_data[warehouse_data['adjustment_out'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Internal In': np.unique(list(
                        warehouse_data[warehouse_data['internal_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Internal Out': np.unique(list(
                        warehouse_data[warehouse_data['internal_out'] > 0].groupby('product_name').groups.keys())).size,
                    'Production In': np.unique(list(warehouse_data[warehouse_data['production_in'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Production Out': np.unique(list(warehouse_data[warehouse_data['production_out'] > 0].groupby(
                        'product_name').groups.keys())).size
                }
            })

        total_category_name = np.unique(current_company_stock_movement_data.category_name.values).tolist()
        categorized_stock_movement_data = {}
        for category_name in total_category_name:
            category_data = current_company_stock_movement_data[current_company_stock_movement_data['category_name'].isin([category_name])]

            categorized_stock_movement_data.update({
                category_name: {
                    'Sales': np.unique(
                        list(category_data[category_data['sales'] > 0].groupby('product_name').groups.keys())).size,
                    'Sales Return': np.unique(list(
                        category_data[category_data['sales_return'] > 0].groupby('product_name').groups.keys())).size,
                    'Purchase': np.unique(
                        list(category_data[category_data['purchase'] > 0].groupby('product_name').groups.keys())).size,
                    'Purchase Return': np.unique(list(category_data[category_data['purchase_return'] > 0].groupby(
                        'product_name').groups.keys())).size,
                    'Transit In': np.unique(list(
                        category_data[category_data['transit_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Transit Out': np.unique(list(
                        category_data[category_data['transit_out'] > 0].groupby('product_name').groups.keys())).size,
                    'Opening Stock': np.unique(list(
                        category_data[category_data['opening_stock'] > 0].groupby('product_name').groups.keys())).size,
                    'Closing Stock': np.unique(
                        list(category_data[category_data['closing'] > 0].groupby('product_name').groups.keys())).size,
                    'Adjustment In': np.unique(list(
                        category_data[category_data['adjustment_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Adjustment Out': np.unique(list(
                        category_data[category_data['adjustment_out'] > 0].groupby('product_name').groups.keys())).size,
                    'Internal In': np.unique(list(
                        category_data[category_data['internal_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Internal Out': np.unique(list(
                        category_data[category_data['internal_out'] > 0].groupby('product_name').groups.keys())).size,
                    'Production In': np.unique(list(
                        category_data[category_data['production_in'] > 0].groupby('product_name').groups.keys())).size,
                    'Production Out': np.unique(list(
                        category_data[category_data['production_out'] > 0].groupby('product_name').groups.keys())).size
                }
            })

        result = {
            'final_action_click': final_action_click,
            'total_product_count': total_product_count,
            'total_sale_stock': sale_total_product,
            'total_sale_return_stock': sale_return_total_product,
            'total_purchase_stock': purchase_total_product,
            'total_purchase_return_stock': purchase_return_total_product,
            'total_adjustment_in_stock': adjustment_in_total_product,
            'total_adjustment_out_stock': adjustment_out_total_product,
            'total_category_name': total_category_name,
            'warehouse_stock_movement_data': warehouse_stock_movement_data,
            'categorized_stock_movement_data': categorized_stock_movement_data,
        }

        return result