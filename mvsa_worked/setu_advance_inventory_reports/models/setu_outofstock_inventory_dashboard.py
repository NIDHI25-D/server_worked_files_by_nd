from odoo import fields, models, api, _
from datetime import datetime


class SetuOutOfStockDashboard(models.Model):
    _name = 'setu.out.of.stock.dashboard'
    _description = 'Setu Out of Stock Analysis Dashboard'

    @api.model
    def return_out_of_stock_analysis(self, start_dt=None, end_dt=None, adv_stock_days = None):
        """
            Added By: Shivam Pandya | Date: 23 dec,2024 | Task: 1292
            Use: prepare data and returns dict to pass in JS for graphs
        """
        company = self.env.company
        company_currency_symbol = company.currency_id.symbol
        start_date = start_dt if start_dt else datetime.today().replace(month=1, day=1).date().strftime('%Y-%m-%d')
        end_date = end_dt if end_dt else datetime.today().replace(month=12, day=31).date().strftime('%Y-%m-%d')
        advance_stock_days = adv_stock_days if adv_stock_days else '30'

        line_action = self.env['setu.inventory.outofstock.report'].create({
            'company_ids': company,
            'advance_stock_days': advance_stock_days,
            'start_date': start_date,
            'end_date': end_date
        })

        final_line_action = line_action.download_report_in_listview()

        wizard_id = final_line_action.get('domain')[0][2]
        data = self.env['setu.inventory.outofstock.bi.report'].search([('wizard_id', '=', wizard_id)])
        total_prod = self.env['product.product'].search([])
        total_prod_count = len(total_prod)
        total_prod_valuation = 0
        total_prod_valuation += sum(
            prod.standard_price * prod.qty_available for prod in total_prod if prod.qty_available > 0)

        out_of_stock_product_ids = set([item.product_id.id for item in data if item.out_of_stock_qty > 0])
        out_of_stock_product_count = len(out_of_stock_product_ids)
        out_of_stock_valuation = sum([item.out_of_stock_value for item in data if item.out_of_stock_qty > 0])

        overall_stock_valuation = 0
        out_of_stock_qty_by_product_category = {}
        out_of_stock_qty_by_warehouse = {}

        for line in data:
            product_id = self.env['product.product'].browse(line.product_id.id)
            category_name = self.env['product.category'].browse(line.product_category_id.id).name
            warehouse_name = self.env['stock.warehouse'].browse(line.warehouse_id.id).name
            qty_available = line.qty_available

            if category_name not in out_of_stock_qty_by_product_category:
                out_of_stock_qty_by_product_category[category_name] = [0, 1]
            if warehouse_name not in out_of_stock_qty_by_warehouse:
                out_of_stock_qty_by_warehouse[warehouse_name] = [0, 1]

            if line.out_of_stock_qty > 0:
                out_of_stock_qty_by_product_category[category_name][0] += 1
                out_of_stock_qty_by_warehouse[warehouse_name][0] += 1

                out_of_stock_value = line.out_of_stock_qty
                out_of_stock_qty_by_product_category[category_name][1] += out_of_stock_value
                out_of_stock_qty_by_warehouse[warehouse_name][1] += out_of_stock_value

            if (qty_available and qty_available > 0) and product_id.standard_price:
                overall_stock_valuation += line.qty_available * product_id.standard_price

        total_prod_valuation = int(total_prod_valuation)
        out_of_stock_valuation = round(out_of_stock_valuation, 2)

        out_of_stock_qty_by_stock_movement = {}
        product_ids = self.env['product.product'].browse(out_of_stock_product_ids)

        line_action = self.env['setu.inventory.fsn.company.wise.report'].create({
            'dashboard_id': self.id,
            'company_ids': self.env.companies.ids,
            'product_ids': product_ids.ids,
            'start_date': start_date,
            'end_date': end_date
        })

        final_action = line_action.download_report_in_listview()
        dashboard_id = final_line_action.get('domain')[0][2]
        fsn_data = self.env['setu.inventory.fsn.company.wise.report'].search([('dashboard_id', '=', dashboard_id)])

        for line in fsn_data:
            stock_movement = line.stock_movement
            if stock_movement not in out_of_stock_qty_by_stock_movement:
                out_of_stock_qty_by_stock_movement[stock_movement] = 0
            out_of_stock_qty_by_stock_movement[stock_movement] += 1


        query = """
                        Select * from get_inventory_fsn_analysis_report_company_vise('%s','%s','%s','%s','%s','%s','%s')
                    """ % ({company.id}, set(out_of_stock_product_ids) if out_of_stock_product_ids else {}, {}, {}, start_date, end_date, 'all')
        self._cr.execute(query)
        fsn_data = self._cr.dictfetchall()


        for line in fsn_data:
            stock_movement = line.get('stock_movement')
            if stock_movement not in out_of_stock_qty_by_stock_movement:
                out_of_stock_qty_by_stock_movement[stock_movement] = 0
            out_of_stock_qty_by_stock_movement[stock_movement] += 1


        dict = {
            'company_currency_symbol': company_currency_symbol,
            'total_prod': total_prod_count,
            'overall_stock_valuation': total_prod_valuation,
            'out_of_stock_product_count': out_of_stock_product_count,
            'out_of_stock_valuation': out_of_stock_valuation,
            'out_of_stock_qty_by_product_category': out_of_stock_qty_by_product_category,
            'out_of_stock_qty_by_warehouse': out_of_stock_qty_by_warehouse,
            'out_of_stock_qty_by_stock_movement': out_of_stock_qty_by_stock_movement,
            'final_line_action': final_line_action,
            'final_action': final_action,
        }

        return dict