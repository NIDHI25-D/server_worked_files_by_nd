from odoo import fields, models, api, _


class SetuInventoryFSNCompanyWiseReport(models.TransientModel):
    _name = 'setu.inventory.fsn.company.wise.report'
    _description = 'Inventory FSN Company Wise Report For Out of Stock Products'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    dashboard_id = fields.Many2one('setu.out.of.stock.dashboard')
    company_ids = fields.Many2many("res.company", string="Companies")
    product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_ids = fields.Many2many('product.product', string="Products")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses")
    stock_movement_type = fields.Selection([('all', 'All'),
                                            ('fast', 'Fast Moving'),
                                            ('slow', 'Slow Moving'),
                                            ('non', 'Non Moving')], "FSN Classification", default="all")

    def get_inventory_fsn_company_wise_report_data(self):
        """
        :return:
        """
        start_date = self.start_date
        end_date = self.end_date
        category_ids = company_ids = {}
        if self.product_category_ids:
            categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
            category_ids = set(categories.ids) or {}
        products = self.product_ids and set(self.product_ids.ids) or {}

        if self.company_ids:
            companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
            company_ids = set(companies.ids) or {}
        else:
            company_ids = set(self.env.context.get('allowed_company_ids', False) or self.env.user.company_ids.ids) or {}

        warehouses = self.warehouse_ids and set(self.warehouse_ids.ids) or {}

        query = """
                Select * from get_inventory_fsn_analysis_report_company_vise('%s','%s','%s','%s','%s','%s', '%s')
            """ % (company_ids, products, category_ids, warehouses, start_date, end_date, self.stock_movement_type)
        self._cr.execute(query)
        stock_data = self._cr.dictfetchall()
        return stock_data


    def download_report_in_listview(self):
        stock_data = self.get_inventory_fsn_company_wise_report_data()
        # print (stock_data)
        for fsn_data_value in stock_data:
            fsn_data_value['dashboard_id'] = self.id
            self.create_data(fsn_data_value)

        graph_view_id = self.env.ref(
            'setu_advance_inventory_reports.setu_inventory_fsn_company_wise_bi_report_graph').id
        tree_view_id = self.env.ref('setu_advance_inventory_reports.setu_inventory_fsn_company_wise_bi_report_tree').id
        is_graph_first = self.env.context.get('graph_report', False)
        report_display_views = []
        viewmode = 'list'
        if is_graph_first:
            report_display_views.append((graph_view_id, 'graph'))
            report_display_views.append((tree_view_id, 'list'))
            viewmode = "graph,list"
        else:
            report_display_views.append((tree_view_id, 'list'))
            report_display_views.append((graph_view_id, 'graph'))
            viewmode = "list,graph"
        return {
            'name': _('Inventory FSN Company Wise Analysis'),
            'domain': [('dashboard_id', '=', self.id)],
            'res_model': 'setu.inventory.fsn.company.wise.bi.report',
            'view_mode': viewmode,
            'type': 'ir.actions.act_window',
            'views': report_display_views,
        }

    def create_data(self, data):
        del data['company_name']
        del data['product_name']
        del data['category_name']
        return self.env['setu.inventory.fsn.company.wise.bi.report'].create(data)


class SetuInventoryFSNCompanyWiseBIReport(models.TransientModel):
    _name = 'setu.inventory.fsn.company.wise.bi.report'
    _description = """Inventory FSN Analysis Report for Out of Stock Products"""

    company_id = fields.Many2one("res.company", "Company")
    product_id = fields.Many2one("product.product", "Product")
    product_category_id = fields.Many2one("product.category", "Category")
    opening_stock = fields.Float("Opening Stock")
    closing_stock = fields.Float("Closing Stock")
    average_stock = fields.Float("Average Stock")
    sales = fields.Float("Sales")
    turnover_ratio = fields.Float("Turnover Ratio")
    stock_movement = fields.Char("FSN Classification")
    dashboard_id = fields.Many2one("setu.inventory.fsn.company.wise.report")
