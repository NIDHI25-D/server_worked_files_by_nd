from datetime import datetime
from odoo import fields, models, api, _


class SetuInventoryLedger(models.TransientModel):
    _name = 'setu.inventory.ledger.report'
    _description = "Inventory Ledger Report"

    stock_file_data = fields.Binary('Stock Movement File')
    start_date = fields.Date(string="Start Date", default=datetime.today().replace(day=1))
    end_date = fields.Date(string="End Date", default=datetime.today())
    product_category_ids = fields.Many2many("product.category", string="Product Categories")
    product_ids = fields.Many2many("product.product", 'inventory_ledger_product_rel', 'inventory_report_id',
                                      'product_id', string="Products")
    products_ids = fields.Many2many("product.product", 'inventory_ledger_products_rel', 'inventory_report_id',
                                      'products_id', string="Products", compute="_compute_products_ids")
    warehouse_ids = fields.Many2many("stock.warehouse", 'inventory_ledger_warehouse_rel', 'inv_report_id', 'warehouse_id', string="Warehouses")
    warehouses_ids = fields.Many2many("stock.warehouse", 'inventory_ledger_warehouses_rel', 'inventory_report_id',
                                      'warehouses_id', string="Warehouses", compute="_compute_warehouses_ids")
    # stock_location = fields.Many2many("stock.location", string="Stock Location")
    company_ids = fields.Many2many("res.company", string="Companies")
    report_by = fields.Selection([('company_wise', 'Company'),
                                  ('warehouse_wise', 'Warehouse')], "Report by", default="warehouse_wise")

    @api.depends('company_ids')
    def _compute_warehouses_ids(self):
        for record in self:
            if record.company_ids:
                warehouses = self.env['stock.warehouse'].search(
                    [('partner_id', 'child_of', record.company_ids.mapped('partner_id').ids)])
                record.warehouses_ids = warehouses if warehouses else False
            else:
                warehouses = self.env['stock.warehouse'].search([])
                record.warehouses_ids = warehouses if warehouses else False

    # @api.onchange('company_ids')
    # def onchange_company_id(self):
    #     if self.company_ids:
    #         return {
    #             'domain': {'warehouse_ids': [('partner_id', 'child_of', self.company_ids.mapped('partner_id').ids)]}}

    @api.depends('product_category_ids')
    def _compute_products_ids(self):
        for record in self:
            if record.product_category_ids:
                products = self.env['product.product'].search(
                    [('categ_id', 'child_of', record.product_category_ids.ids)])
                record.products_ids = products if products else False
            else:
                products = self.env['product.product'].search([])
                record.products_ids = products if products else False

    # @api.onchange('product_category_ids')
    # def onchange_product_category_id(self):
    #     if self.product_category_ids:
    #         return {'domain': {'product_ids': [('categ_id', 'child_of', self.product_category_ids.ids)]}}

    def download_report_in_listview(self):
        stock_data = self.get_products_movements_for_inventory_ledger()
        # print(stock_data)
        # for ledger_data_value in stock_data:
        #     ledger_data_value['wizard_id'] = self.id
        #     self.create_data(ledger_data_value)

        # graph_view_id = self.env.ref('setu_inventory_ledger_report.setu_inventory_fsn_analysis_bi_report_graph').id
        list_view_id = self.env.ref('setu_inventory_ledger_report.setu_inventory_ledger_bi_report_list').id
        list_view_id_cmpwise = self.env.ref('setu_inventory_ledger_report.setu_inventory_ledger_bi_report_list_cmpwise').id
        form_view_id = self.env.ref('setu_inventory_ledger_report.setu_inventory_ledger_bi_report_form').id
        search_view = self.env.ref(
            'setu_inventory_ledger_report.setu_inventory_ledger_bi_report_searchview_for_company').id \
                if self.report_by == 'company_wise' else self.env.ref(
            'setu_inventory_ledger_report.setu_inventory_ledger_bi_report_searchview').id
        # is_graph_first = self.env.context.get('graph_report', False)
        report_display_views = []
        list_id = list_view_id
        if self.report_by == 'company_wise':
            list_id = list_view_id_cmpwise

        report_display_views.append((list_id, 'list'))
        report_display_views.append((form_view_id, 'form'))
        view_mode = "list,form"
        return {
            'name': _('Invetory Ledger Report - %s to %s' % (self.start_date, self.end_date)),
            'domain': [('wizard_id', '=', self.id)],
            'res_model': 'setu.inventory.ledger.bi.report',
            'search_view_id': [search_view, 'search'],
            'view_mode': view_mode,
            'type': 'ir.actions.act_window',
            'views': report_display_views,
            'context': {'search_default_product_groupby': 1},
            'help': """
                <p class="o_view_nocontent_smiling_face">
                    No data found.
                </p>
            """
        }

    def create_data(self, data):
        del data['product_name']
        del data['company_name']
        if self.report_by == 'warehouse_wise':
            del data['warehouse_name']
        del data['row_id']
        del data['category_name']
        # domain1 = []
        # from_date = data.get('inventory_date').strftime('%Y-%m-%d') + " 00:00:00"
        # to_date = data.get('inventory_date').strftime('%Y-%m-%d') + " 23:59:59"
        # domain = [('state', '=', 'done'), ('product_id', '=', data.get('product_id')), ('date', '>=', from_date),
        #           ('date', '<=', to_date)]
        # if self.report_by == "company_wise":
        #     domain.append(('company_id', '=', data.get('company_id')))
        # else:
        #     warehouse = self.env['stock.warehouse'].browse(data.get('warehouse_id'))
        #     location_ids = self.env['stock.location'].search(
        #         [('id', 'child_of', warehouse.view_location_id.id)]).ids
        #     domain1 = ['|', ('location_id', 'in', location_ids), ('location_dest_id', 'in', location_ids)]
        #
        # move_ids = self.env['stock.move'].search(domain + domain1).ids
        # if move_ids:
        #     data.update({'ledger_detail_ids': [(6, 0, move_ids)]})
        return self.env['setu.inventory.ledger.bi.report'].create(data)

    def get_products_movements_for_inventory_ledger(self):
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

        if self.report_by == 'warehouse_wise':
            # get_products_movements_for_inventory_ledger(integer[], integer[], integer[], integer[], date, date)
            query = """
                    Select * from si_ledger_get_products_movements_for_inventory_ledger('%s','%s','%s','%s','%s','%s','%d')
                """ % (company_ids, products, category_ids, warehouses, start_date, end_date, self.id)
        else:
            # get_products_movements_for_inventory_ledger_cmpwise(integer[], integer[], integer[], date, date)
            query = """
                    Select * from si_ledger_get_products_movements_for_inventory_ledger_cmpwise('%s','%s','%s','%s','%s', '%d')
                """ % (company_ids, products, category_ids, start_date, end_date, self.id)

        self._cr.execute(query)
        stock_data = self._cr.dictfetchall()
        return stock_data

    def prepare_data_to_write(self, stock_data={}):
        """
        :param stock_data:
        :return:
        """
        warehouse_wise_data = {}
        for data in stock_data:
            key = (data.get('warehouse_id'), data.get('warehouse_name'))
            if not warehouse_wise_data.get(key, False):
                warehouse_wise_data[key] = {data.get('product_id'): data}
            else:
                warehouse_wise_data.get(key).update({data.get('product_id'): data})
        return warehouse_wise_data


