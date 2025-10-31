from odoo import fields, models, api

SELECTED_PRODUCTS = set()


class InventoryWarehouseReport(models.TransientModel):
    _name = 'inventory.warehouse.report'
    _description = 'inventory.warehouse.report'

    company_ids = fields.Many2many('res.company', string='Companies')
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    product_ids = fields.Many2many('product.product', string='Products')
    product_id = fields.Many2one('product.product')
    active = fields.Boolean(default=True)
    uom = fields.Many2one(related='product_id.uom_id')
    value = fields.Float('Value')
    qty = fields.Float('OnHand Stock')
    avai_qty = fields.Float('Available Stock')
    company_id = fields.Many2one('res.company')
    warehouse_id = fields.Many2one('stock.warehouse')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    is_published = fields.Boolean(related='product_id.is_published')
    categ_id = fields.Many2one(related='product_id.categ_id')
    #product_brand model
    product_brand_id = fields.Many2one(related='product_id.product_brand_id')#
    crm_tags_ids = fields.Many2many(related='product_id.crm_tags_ids')#
    #marvelfields model
    temporary_id = fields.Many2one(related='product_id.temporary_id')#
    product_type_marvelsa = fields.Selection(related='product_id.product_type_marvelsa')#
    #setu_price_update model
    import_factor_level_id = fields.Many2one(related='product_id.import_factor_level_id')#
    competition_level_id = fields.Many2one(related='product_id.competition_level_id')#


    def prepare_report_vals(self, values):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/01/25
            Task: Migration from V16 to V18
            Purpose: Prepare values for a report.
        """
        vals = {
            'warehouse_id': values[0],
            'company_id': values[1],
            'product_id': values[2],
            'qty': values[3],
            'avai_qty': values[4],
            'value': values[5]
        }
        SELECTED_PRODUCTS.add(values[2])
        return vals

    def get_product_search_domain(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/01/25
            Task: Migration from V16 to V18
            Purpose: Domain for products.
        """
        if not self.product_ids.ids:
            domain = [('id', 'not in', list(SELECTED_PRODUCTS))]
        else:
            domain = [('id', 'in', list(set(self.product_ids.ids).difference(SELECTED_PRODUCTS)))]

        return domain

    def checker(self, rec):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/01/25
            Task: Migration from V16 to V18
            Purpose: If any of data retrieve from wizard then report will be as per the report.
        """
        if self.warehouse_ids and rec[0] not in self.warehouse_ids.ids:
            return False
        if self.product_ids and rec[2] not in self.product_ids.ids:
            return False
        if self.product_category_ids and rec[6] not in self.product_category_ids.ids:
            return False
        if self.company_ids and rec[1] not in self.company_ids.ids:
            return False
        return True

    def create_report(self, inventory_data):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/01/25
            Task: Migration from V16 to V18
            Purpose: Create a report as per the data retrieve in wizard.
        """
        for rec in inventory_data:
            res = self.checker(rec)
            if res:
                self.create(self.prepare_report_vals(rec))
        product_search_domain = self.get_product_search_domain()
        no_valuation_products = self.env['product.product'].search(product_search_domain)
        if self.product_category_ids:
            no_valuation_products = no_valuation_products.filtered(
                lambda pro: pro.product_tmpl_id.categ_id in self.product_category_ids)
        for product in no_valuation_products:
            self.create({
                'warehouse_id': False,
                'company_id': product.company_id.id,
                'product_id': product.id,
                'qty': 0,
                'avai_qty': 0,
                'value': 0
            })

    def get_inventory_data(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/01/25
            Task: Migration from V16 to V18
            Purpose: To get data from wizard to show in the inventory warehouse valuation report.
        """
        self.active = False
        category_ids = {}
        company_ids = {}
        if self.product_category_ids:
            categories = self.env['product.category'].search([('id', 'child_of', self.product_category_ids.ids)])
            category_ids = set(categories.ids) or {}
        products = self.product_ids and set(self.product_ids.ids) or {}

        if self.company_ids:
            companies = self.env['res.company'].search([('id', 'child_of', self.company_ids.ids)])
            company_ids = set(companies.ids) or {}
        else:
            company_ids = set(self.env.user.company_ids.ids) or {}
        if self.warehouse_ids:
            warehouses = set(self.warehouse_ids.ids)
        else:
            warehouses = {}
        self._cr.execute(
            f"select * from set_inventory_warehouse_wise_data('{company_ids}','{warehouses}','{products}','{category_ids}')")
        inventory_data = self._cr.fetchall()
        self.create_report(inventory_data)

        return {
            'name': 'Inventory Valuation',
            'type': 'ir.actions.act_window',
            'view_mode': 'list, pivot',
            'res_model': 'inventory.warehouse.report',
            'context': {'search_default_group_by_warehouse_id': 1, 'search_default_has_valuation': 1},
            'views': [[self.env.ref('setu_inventory_warehouse_report.view_list_inventory_warehouse_report').id, 'list'],
                      [self.env.ref('setu_inventory_warehouse_report.view_product_pivot_view_report').id, 'pivot']],
        }
