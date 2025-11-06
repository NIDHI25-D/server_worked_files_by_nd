from odoo import fields, models, api, _
from collections import defaultdict
from datetime import datetime


class SetuFSNDashboard(models.Model):
    _name = 'setu.fsn.dashboard'
    _description = 'Setu FSN Dashboard'


    @api.model
    def get_fsn_analysis_data(self, start_dt=None, end_dt=None):
        start_date = start_dt if start_dt else datetime.today().replace(month=1, day=1).date().strftime('%Y-%m-%d')
        end_date = end_dt if end_dt else datetime.today().replace(month=12, day=31).date().strftime('%Y-%m-%d')

        stock_movement_type = 'all'
        category_ids = set()
        product_ids = set()
        company_ids = set()
        warehouse_ids = set()

        line_action = self.env['setu.inventory.fsn.analysis.report'].create({
            'stock_movement_type': 'all', 'start_date': start_date, 'end_date': end_date
        })
        final_line_action = line_action.download_report_in_listview()


        company_ids = set(self.env.user.company_ids.ids)

        # Query to fetch all data from FSN analysis report (excluding company-wise)
        query = """
                SELECT * FROM get_inventory_fsn_analysis_report(%s, %s, %s, %s, %s, %s, %s)
            """
        params = (
            list(company_ids),
            list(product_ids),
            list(category_ids),
            list(warehouse_ids),
            start_date,
            end_date,
            stock_movement_type,
        )

        self._cr.execute(query, params)
        stock_data = self._cr.dictfetchall()

        # Query to fetch company-wise data from the company-specific FSN analysis report
        company_query = """
            WITH stock_data AS (
                SELECT *
                FROM get_inventory_fsn_analysis_report_company_vise(%s, %s, %s, %s, %s, %s, %s)
            ),
            product_count AS (
                SELECT COUNT(DISTINCT product_id) AS total_product_count
                FROM stock_data
            ),
            stock_movement_counts AS (
                SELECT stock_movement,
                       COUNT(DISTINCT product_id) AS product_count
                FROM stock_data
                GROUP BY stock_movement
            )
            SELECT * FROM stock_data, product_count, stock_movement_counts;
        """

        company_params = (
            list(company_ids),
            list(product_ids),
            list(category_ids),
            list(warehouse_ids),
            start_date,
            end_date,
            stock_movement_type,
        )

        self._cr.execute(company_query, company_params)
        company_stock_data = self._cr.dictfetchall()

        total_product_count = company_stock_data[0]['total_product_count'] if company_stock_data else 0

        # Initialize the movement counts
        fast_moving_count = 0
        slow_moving_count = 0
        non_moving_count = 0

        # Parse stock movement counts
        for row in company_stock_data:
            stock_movement = row.get('stock_movement')
            product_count = row.get('product_count', 0)

            if stock_movement == 'Fast Moving':
                fast_moving_count = product_count
            elif stock_movement == 'Slow Moving':
                slow_moving_count = product_count
            elif stock_movement == 'Non Moving':
                non_moving_count = product_count

        # Initialize data structures for categorizing
        category_data = defaultdict(lambda: {
            'fast_moving': 0, 'slow_moving': 0, 'non_moving': 0,
            'fast_moving_count': 0, 'slow_moving_count': 0, 'non_moving_count': 0
        })

        company_data = defaultdict(lambda: {
            'fast_moving': 0, 'slow_moving': 0, 'non_moving': 0,
            'fast_moving_count': 0, 'slow_moving_count': 0, 'non_moving_count': 0
        })

        warehouse_data = defaultdict(lambda: {
            'fast_moving': 0, 'slow_moving': 0, 'non_moving': 0,
            'fast_moving_count': 0, 'slow_moving_count': 0, 'non_moving_count': 0,
            'total_count': 0,
            'fast_moving_percentage': "0%",
            'slow_moving_percentage': "0%",
            'non_moving_percentage': "0%",
        })

        total = {
            'fast_moving': 0,
            'slow_moving': 0,
            'non_moving': 0,
            'fast_moving_count': 0,
            'slow_moving_count': 0,
            'non_moving_count': 0
        }

        category_names = {}

        # Process the stock data (excluding company-specific data)
        for row in stock_data:
            category_name = row.get('category_name', 'Unknown')
            product_category_id = row.get('product_category_id')
            stock_movement = row.get('stock_movement', 'Unknown')
            warehouse_id = row.get('warehouse_id')

            # Add category name if not available
            if product_category_id and product_category_id not in category_names:
                category = self.env['product.category'].browse(product_category_id)
                category_names[product_category_id] = category.name if category else 'Unknown Category'

            # Handle stock movement classification
            if stock_movement == 'Fast Moving':
                category_data[product_category_id]['fast_moving_count'] += 1
                total['fast_moving_count'] += 1

                # Aggregate by warehouse
                if warehouse_id:
                    warehouse_data[warehouse_id]['fast_moving_count'] += 1
                    warehouse_data[warehouse_id]['total_count'] += 1

            elif stock_movement == 'Slow Moving':
                category_data[product_category_id]['slow_moving_count'] += 1
                total['slow_moving_count'] += 1

                # Aggregate by warehouse
                if warehouse_id:
                    warehouse_data[warehouse_id]['slow_moving_count'] += 1
                    warehouse_data[warehouse_id]['total_count'] += 1

            elif stock_movement == 'Non Moving':
                category_data[product_category_id]['non_moving_count'] += 1
                total['non_moving_count'] += 1

                # Aggregate by warehouse
                if warehouse_id:
                    warehouse_data[warehouse_id]['non_moving_count'] += 1
                    warehouse_data[warehouse_id]['total_count'] += 1

        # Calculate percentages for each warehouse
        for warehouse_id, data in warehouse_data.items():
            total_count = data['total_count']
            if total_count > 0:
                data['fast_moving_percentage'] = "{:.2f}%".format((data['fast_moving_count'] / total_count) * 100)
                data['slow_moving_percentage'] = "{:.2f}%".format((data['slow_moving_count'] / total_count) * 100)
                data['non_moving_percentage'] = "{:.2f}%".format((data['non_moving_count'] / total_count) * 100)

        # Process company-wise stock data
        for row in company_stock_data:
            stock_movement = row.get('stock_movement', 'Unknown')
            company_id = row.get('company_id')

            # Handle stock movement classification
            if stock_movement == 'Fast Moving':
                company_data[company_id]['fast_moving_count'] += 1

            elif stock_movement == 'Slow Moving':
                company_data[company_id]['slow_moving_count'] += 1

            elif stock_movement == 'Non Moving':
                company_data[company_id]['non_moving_count'] += 1

        # Calculate percentages for Fast Moving, Slow Moving, and Non Moving products
        if total_product_count > 0:
            fast_moving_percentage = "{:.2f}%".format((fast_moving_count / total_product_count) * 100)
            slow_moving_percentage = "{:.2f}%".format((slow_moving_count / total_product_count) * 100)
            non_moving_percentage = "{:.2f}%".format((non_moving_count / total_product_count) * 100)
        else:
            fast_moving_percentage = "0%"
            slow_moving_percentage = "0%"
            non_moving_percentage = "0%"

        # Compile the result
        result = {
            'final_line_action': final_line_action,
            'total_product_count': total_product_count,
            'fast_moving_count': fast_moving_count,
            'slow_moving_count': slow_moving_count,
            'non_moving_count': non_moving_count,
            'fast_moving_percentage': fast_moving_percentage,
            'slow_moving_percentage': slow_moving_percentage,
            'non_moving_percentage': non_moving_percentage,
            'categories': {
                category_names[category_id]: {
                    'fast_moving_count': data['fast_moving_count'],
                    'slow_moving_count': data['slow_moving_count'],
                    'non_moving_count': data['non_moving_count'],
                }
                for category_id, data in category_data.items()
            },

            'companies': {
                self.env['res.company'].browse(company_id).name: {
                    'fast_moving_count': data['fast_moving_count'],
                    'slow_moving_count': data['slow_moving_count'],
                    'non_moving_count': data['non_moving_count'],
                }
                for company_id, data in company_data.items()
            },

            'warehouses': {
                self.env['stock.warehouse'].browse(warehouse_id).name: {
                    'fast_moving_count': data['fast_moving_count'],
                    'slow_moving_count': data['slow_moving_count'],
                    'non_moving_count': data['non_moving_count'],
                    'total_count': data['total_count'],
                    'fast_moving_percentage': data['fast_moving_percentage'],
                    'slow_moving_percentage': data['slow_moving_percentage'],
                    'non_moving_percentage': data['non_moving_percentage'],
                }
                for warehouse_id, data in warehouse_data.items()
            },

            'totals': total
        }

        return result