from odoo import fields, models, api, _


class SetuInventoryLedgerBIReport(models.TransientModel):
    _name = 'setu.inventory.ledger.bi.report'

    inventory_date = fields.Date("Inventory Date")
    company_id = fields.Many2one("res.company", "Company")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    # stock_location = fields.Many2one("stock.location", "Stock Location")
    product_id = fields.Many2one("product.product", "Product")
    product_category_id = fields.Many2one("product.category", "Category")
    opening_stock = fields.Float("Opening Stock", default=0)
    wizard_id = fields.Many2one("setu.inventory.ledger.report")
    purchase = fields.Float("Purchase", default=0)
    sales = fields.Float("Sales", default=0)
    purchase_return = fields.Float("Purchase Return", default=0)
    sales_return = fields.Float("Sales Return", default=0)
    internal_in = fields.Float("Internal In", default=0)
    internal_out = fields.Float("Internal Out", default=0)
    adjustment_in = fields.Float("Adjustment In", default=0)
    adjustment_out = fields.Float("Adjustment Out", default=0)
    production_in = fields.Float("Production In", default=0)
    production_out = fields.Float("Production Out", default=0)
    transit_in = fields.Float("Transit In", default=0)
    transit_out = fields.Float("Transit Out", default=0)
    closing = fields.Float("Closing", default=0)
    ledger_detail_ids = fields.Many2many("stock.move", string="Product movements", compute='_calculate_ledger_details')
    # total_in = fields.Integer(string='Total in', store=False, readonly=True, compute='_amount_all')
    # total_out = fields.Integer(string='Total out', store=False, readonly=True, compute='_amount_all')
    total_in = fields.Float(string='Total in', default=0)
    total_out = fields.Float(string='Total out', default=0)
    product_movements = fields.Selection(
        [('all', "All"), ('purchase', "Purchase"), ('purchase_return', "Purchase Return"),
         ('sales', "Sales"), ('sales_return', "Sales Return"),
         ('internal_in', "Internal in"), ('internal_out', "Internal out"),
         ('adjustment_in', "Adjustment in"), ('adjustment_out', "Adjustment out"),
         ('transit_in', "Transit in"), ('transit_out', "Transit out"),
         ('production_in', "Production in"), ('production_out', "Production out"),
         ], "Choose movement", default="all")

    def _compute_display_name(self):
        for record in self:
            record.display_name = 'Ledger Report Movement [{}]'.format(record.inventory_date)

    @api.depends('product_movements')
    def _calculate_ledger_details(self):
        domain1 = []
        self.ledger_detail_ids = []
        from_date = self.inventory_date.strftime('%Y-%m-%d') + " 00:00:00"
        to_date = self.inventory_date.strftime('%Y-%m-%d') + " 23:59:59"
        domain = [('state', '=', 'done'), ('product_id', '=', self.product_id.id), ('date', '>=', from_date),
                  ('date', '<=', to_date)]
        if self.wizard_id.report_by == "company_wise":
            domain.append(('company_id', '=', self.company_id.id))
        else:
            warehouse = self.env['stock.warehouse'].browse(self.warehouse_id.id)
            location_ids = self.env['stock.location'].search(
                [('id', 'child_of', warehouse.view_location_id.id)]).ids
            domain1 = ['|', ('location_id', 'in', location_ids), ('location_dest_id', 'in', location_ids)]

        if self.product_movements == "purchase":
            domain.append(('location_id.usage', '=', 'supplier'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "purchase_return":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'supplier'))
        elif self.product_movements == "sales":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'customer'))
        elif self.product_movements == "sales_return":
            domain.append(('location_id.usage', '=', 'customer'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "internal_in" or self.product_movements == "internal_out":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "adjustment_in":
            domain.append(('location_id.usage', '=', 'inventory'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "adjustment_out":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'inventory'))
        elif self.product_movements == "transit_in":
            domain.append(('location_id.usage', '=', 'transit'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "transit_out":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'transit'))
        elif self.product_movements == "production_in":
            domain.append(('location_id.usage', '=', 'production'))
            domain.append(('location_dest_id.usage', '=', 'internal'))
        elif self.product_movements == "production_out":
            domain.append(('location_id.usage', '=', 'internal'))
            domain.append(('location_dest_id.usage', '=', 'production'))

        move_ids = self.env['stock.move'].search(domain + domain1).ids
        if move_ids:
            self.write({'ledger_detail_ids': [(6, 0, move_ids)]})

    # def _amount_all(self):
    #     for movement in self:
    #         movement.total_in = movement.purchase + movement.sales_return + movement.internal_in + movement.adjustment_in + movement.production_in + movement.transit_in
    #         movement.total_out = movement.purchase_return + movement.sales + movement.internal_out + movement.adjustment_out + movement.production_out + movement.transit_out

    def action_bypass_form_view(self):
        return False
