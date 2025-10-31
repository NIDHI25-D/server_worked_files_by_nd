from odoo import fields, models, api, _
from collections import defaultdict


class SetuInventoryAgeBreakdownDashboard(models.Model):
    _name = 'setu.age.breakdown.inventory.dashboard'
    _description = 'Setu Age Breakdown Inventory Dashboard'

    @api.model
    def get_inventory_data(self):
        product_ids = set()
        company_ids = set(self.env.companies.ids)
        category_ids = set()

        company = self.env.company
        company_currency_symbol = company.currency_id.symbol

        breakdown_line_action = self.env['setu.inventory.age.breakdown.report']
        final_breakdown_action = breakdown_line_action.download_report_in_listview()

        age_line_action = self.env['setu.inventory.age.report']
        final_age_action = age_line_action.download_report_in_listview()

        query = """
                SELECT
                    ir.product_category_id,
                    pc.name AS category_name,
                    ir.company_id,
                    ir.days_old,
                    ir.current_stock,
                    ir.current_stock_value,
                    ir.oldest_stock_qty,
                    ir.oldest_stock_value
                FROM inventory_stock_age_report(%s, %s, %s) ir
                LEFT JOIN product_category pc ON ir.product_category_id = pc.id
            """

        params = (
            list(company_ids),
            list(product_ids),
            list(category_ids),
        )

        self._cr.execute(query, params)
        stock_data = self._cr.dictfetchall()


        total_product_count = len(stock_data)
        total_days_old = 0
        total_current_stock = 0
        total_current_stock_value = 0
        total_oldest_stock_qty = 0
        total_oldest_stock_value = 0
        category_totals = defaultdict(lambda: {
            'total_stock_qty': 0,
            'total_stock_value': 0,
            'category_name': ''
        })
        company_totals = defaultdict(lambda: {
            'total_stock_qty': 0,
            'total_stock_value': 0,
            'company_name': ''
        })
        for row in stock_data:
            total_days_old += row.get('days_old', 0)
            total_current_stock += row.get('current_stock', 0)
            total_current_stock_value += row.get('current_stock_value', 0)
            total_oldest_stock_qty += row.get('oldest_stock_qty', 0)
            total_oldest_stock_value += row.get('oldest_stock_value', 0)
            product_category_id = row.get('product_category_id')
            category_name = row.get('category_name')
            if product_category_id:
                category_totals[product_category_id]['total_stock_qty'] += row.get('oldest_stock_qty', 0)
                category_totals[product_category_id]['total_stock_value'] += row.get('oldest_stock_value', 0)
                category_totals[product_category_id]['category_name'] = category_name
            company_id = row.get('company_id')
            if company_id:
                company_name = self.env['res.company'].browse(company_id).name
                company_totals[company_id]['total_stock_qty'] += row.get('oldest_stock_qty', 0)
                company_totals[company_id]['total_stock_value'] += row.get('oldest_stock_value', 0)
                company_totals[company_id]['company_name'] = company_name
        total_oldest_stock_value = round(total_oldest_stock_value, 2)
        total_current_stock_value = round(total_current_stock_value, 2)
        breakdown_days = self.env.context.get('breakdown_days', 30)
        breakdown_query = """
                    SELECT *
                    FROM get_inventory_age_breakdown_data(%s, %s, %s, %s)
            """
        breakdown_params = (
            list(company_ids) or None,
            list(product_ids) or None,
            list(category_ids) or None,
            breakdown_days
        )
        self._cr.execute(breakdown_query, breakdown_params)
        breakdown_result = self._cr.dictfetchall()

        total_stock = sum(row.get('total_stock', 0) for row in breakdown_result)
        breakdown1_qty = sum(row.get('breakdown1_qty', 0) for row in breakdown_result)
        breakdown2_qty = sum(row.get('breakdown2_qty', 0) for row in breakdown_result)
        breakdown3_qty = sum(row.get('breakdown3_qty', 0) for row in breakdown_result)
        breakdown4_qty = sum(row.get('breakdown4_qty', 0) for row in breakdown_result)
        breakdown5_qty = sum(row.get('breakdown5_qty', 0) for row in breakdown_result)
        breakdown6_qty = sum(row.get('breakdown6_qty', 0) for row in breakdown_result)
        breakdown7_qty = sum(row.get('breakdown7_qty', 0) for row in breakdown_result)
        category_data = {}
        for row in breakdown_result:
            category_id = row.get('product_category_id')
            category_name = row.get('category_name', 'Undefined')
            if category_id not in category_data:
                category_data[category_id] = {
                    'category_name': category_name,
                    'total_breakdown1_qty': 0,
                    'total_breakdown2_qty': 0,
                    'total_breakdown3_qty': 0,
                    'total_breakdown4_qty': 0,
                    'total_breakdown5_qty': 0,
                    'total_breakdown6_qty': 0,
                    'total_breakdown7_qty': 0,
                    'total_breakdown_qty': 0
                }
            category_data[category_id]['total_breakdown1_qty'] += row.get('breakdown1_qty', 0)
            category_data[category_id]['total_breakdown2_qty'] += row.get('breakdown2_qty', 0)
            category_data[category_id]['total_breakdown3_qty'] += row.get('breakdown3_qty', 0)
            category_data[category_id]['total_breakdown4_qty'] += row.get('breakdown4_qty', 0)
            category_data[category_id]['total_breakdown5_qty'] += row.get('breakdown5_qty', 0)
            category_data[category_id]['total_breakdown6_qty'] += row.get('breakdown6_qty', 0)
            category_data[category_id]['total_breakdown7_qty'] += row.get('breakdown7_qty', 0)
            total_breakdown_qty = sum([
                row.get('breakdown1_qty', 0),
                row.get('breakdown2_qty', 0),
                row.get('breakdown3_qty', 0),
                row.get('breakdown4_qty', 0),
                row.get('breakdown5_qty', 0),
                row.get('breakdown6_qty', 0),
                row.get('breakdown7_qty', 0)
            ])
            category_data[category_id]['total_breakdown_qty'] += total_breakdown_qty
        category_summary = [
            {
                'category_id': category_id,
                'category_name': data['category_name'],
                'total_breakdown1_qty': data['total_breakdown1_qty'],
                'total_breakdown2_qty': data['total_breakdown2_qty'],
                'total_breakdown3_qty': data['total_breakdown3_qty'],
                'total_breakdown4_qty': data['total_breakdown4_qty'],
                'total_breakdown5_qty': data['total_breakdown5_qty'],
                'total_breakdown6_qty': data['total_breakdown6_qty'],
                'total_breakdown7_qty': data['total_breakdown7_qty'],
                'total_breakdown_qty': data['total_breakdown_qty'],
            }
            for category_id, data in category_data.items()
        ]
        product_breakdown_totals = []
        for row in breakdown_result:
            company = self.env['res.company'].browse(row.get('company_id'))
            oldest_stock_days = company.oldest_stock_days
            total_stock_qty = 0
            if oldest_stock_days == '30_days':
                total_stock_qty = sum([
                    row.get('breakdown2_qty', 0),
                    row.get('breakdown3_qty', 0),
                    row.get('breakdown4_qty', 0),
                    row.get('breakdown5_qty', 0),
                    row.get('breakdown6_qty', 0),
                    row.get('breakdown7_qty', 0)
                ])
            elif oldest_stock_days == '60_days':
                total_stock_qty = sum([
                    row.get('breakdown3_qty', 0),
                    row.get('breakdown4_qty', 0),
                    row.get('breakdown5_qty', 0),
                    row.get('breakdown6_qty', 0),
                    row.get('breakdown7_qty', 0)
                ])
            elif oldest_stock_days == '90_days':
                total_stock_qty = sum([
                    row.get('breakdown4_qty', 0),
                    row.get('breakdown5_qty', 0),
                    row.get('breakdown6_qty', 0),
                    row.get('breakdown7_qty', 0)
                ])
            elif oldest_stock_days == '120_days':
                total_stock_qty = sum([
                    row.get('breakdown5_qty', 0),
                    row.get('breakdown6_qty', 0),
                    row.get('breakdown7_qty', 0)
                ])
            elif oldest_stock_days == '150_days':
                total_stock_qty = sum([
                    row.get('breakdown6_qty', 0),
                    row.get('breakdown7_qty', 0)
                ])
            elif oldest_stock_days == '180_days':
                total_stock_qty = row.get('breakdown7_qty', 0)
            product_name = self.env['product.product'].browse(row.get('product_id')).name
            product_breakdown = {
                'product_id': row.get('product_id'),
                'product_name': product_name,
                'category_name': row.get('category_name'),
                'total_breakdown_qty': total_stock_qty
            }
            product_breakdown_totals.append(product_breakdown)
        product_breakdown_totals = sorted(product_breakdown_totals, key=lambda x: x['total_breakdown_qty'],
                                          reverse=True)
        top_20_products = product_breakdown_totals[:20]


        return {
            'final_breakdown_action': final_breakdown_action,
            'final_age_action': final_age_action,
            'total_product_count': total_product_count,
            'total_days_old': total_days_old,
            'total_current_stock': total_current_stock,
            'total_current_stock_value': total_current_stock_value,
            'total_oldest_stock_qty': total_oldest_stock_qty,
            'total_oldest_stock_value': total_oldest_stock_value,
            'categories': {
                category_id: {
                    'category_name': data['category_name'],
                    'total_stock_qty': round(data['total_stock_qty'], 2),
                    'total_stock_value': round(data['total_stock_value'], 2)
                }
                for category_id, data in category_totals.items()
            },
            'companies': {
                company_id: {
                    'company_name': data['company_name'],
                    'total_stock_qty': round(data['total_stock_qty'], 2),
                    'total_stock_value': round(data['total_stock_value'], 2)
                }
                for company_id, data in company_totals.items()
            },
            'total_stock': total_stock,
            'breakdown1_qty': breakdown1_qty,
            'breakdown2_qty': breakdown2_qty,
            'breakdown3_qty': breakdown3_qty,
            'breakdown4_qty': breakdown4_qty,
            'breakdown5_qty': breakdown5_qty,
            'breakdown6_qty': breakdown6_qty,
            'breakdown7_qty': breakdown7_qty,
            'category_summary': category_summary,
            'top_20_products': top_20_products,
            'product_breakdown_totals': product_breakdown_totals,
            'company_currency_symbol': company_currency_symbol,
        }