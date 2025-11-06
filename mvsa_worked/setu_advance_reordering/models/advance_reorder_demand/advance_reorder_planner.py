from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from statistics import mean
from odoo.exceptions import ValidationError


class AdvanceReorderPlanner(models.Model):
    _name = 'advance.reorder.planner'
    _inherit = ['mail.thread']
    _description = "Advance reorder by demand generation planner"

    def _compute_reorder_count(self):
        for record in self:
            record.reorder_count = len(record.reorder_ids.ids)

    def _compute_purchase_count(self):
        for record in self:
            record.purchase_count = len(record.purchase_ids.ids)

    name = fields.Char("Name", help="Reorder Planner Number")
    vendor_selection_strategy = fields.Selection([('sequence', 'Sequence Of Vendor'),
                                                  ("price", "Cheapest vendor"),
                                                  ("delay", "Quickest vendor"),
                                                  ("specific_vendor", "Specific vendor")],
                                                 string="Vendor selection strategy", default="sequence",
                                                 help="""This field is useful when purchase order is created from order points 
                                                           that time system checks about the vendor which is suitable for placing an order 
                                                           according to need. Whether quickest vendor, cheapest vendor or specific vendor is suitable 
                                                           for the product"""
                                                 )
    state = fields.Selection([('draft', 'Draft'),
                              ('verified', 'Verified')],
                             default="draft", string="Status",
                             help="To identify process status", tracking=True)
    vendor_id = fields.Many2one('res.partner', string="Vendor",
                                help="Set the vendor to whom you want to place an order")
    user_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user,
                              help="Responsible user")
    buffer_security_days = fields.Integer('Coverage days',
                                          help="Place order for next x days, "
                                               "system will generate demands for next x days after order transit time")
    reorder_demand_growth = fields.Float('Expected growth (%)',
                                         help="Add percentage value if you want to calculate demand with growth")
    generate_demand_with = fields.Selection([('history_sales', 'History Sales'),
                                             ('forecast_sales', 'Forecast Sales')],
                                            string="Demand calculation by",
                                            help="Demand generate based on past sales or forecasted sales",
                                            default='history_sales')
    product_ids = fields.Many2many("product.product", string="Products")
    products_ids = fields.Many2many("product.product", 'reorder_planner_products_rel', 'planner_id', 'products_id',
                                    string="Products",
                                    compute="_compute_products_ids", store=True)
    config_ids = fields.One2many('advance.reorder.orderprocess.config', 'reorder_process_template_id',
                                 string='Reorder configuration', help="Reorder configuration")
    auto_workflow_id = fields.Many2one("advance.reorder.process.auto.workflow", string='Auto Workflow')
    past_days = fields.Integer(string="Past Days", default=365)

    planing_frequency = fields.Integer("Planing Frequency Day")
    next_execution_date = fields.Date("Next Execution Date", default=fields.Date.today)
    previous_execution_date = fields.Date("Previous Execution Date", default=fields.Date.today)
    reorder_count = fields.Integer("Reorder Count", compute="_compute_reorder_count")
    reorder_ids = fields.One2many("advance.reorder.orderprocess", "reorder_planner_id", string="Reorder")
    purchase_ids = fields.One2many('purchase.order', 'reorder_planner_id', string='Purchase orders')
    purchase_count = fields.Integer("purchase Count", compute="_compute_purchase_count")
    active = fields.Boolean(default=True)
    only_out_of_stock_product = fields.Boolean("Only Execute for Out of Stock Product")
    reorder_date = fields.Datetime('Reorder date', help="Reorder date", default=datetime.now())
    purchase_order_type = fields.Selection(
        string='Purchase Order Type',
        selection=[('in_stock', 'In Stock'),
                   ('pre_sale', 'Pre Sale'),
                   ('pre_order', 'Pre Order')])

    @api.constrains('purchase_order_type')
    def _check_po_type(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 08/01/25
            Task: Migration to v18 from v16
            Purpose: add constrain if in lines there are a presale products and set Purchase Order Type as a preorder same as for preorder.
        """
        for rec in self:
            if rec.purchase_order_type == 'pre_sale' and rec.product_ids.filtered(lambda x: x.available_for_preorder):
                raise UserError(f"You can not set Pre-Order products to the pre_sale.")
            elif rec.purchase_order_type == 'pre_order' and rec.product_ids.filtered(lambda x: x.available_for_presale):
                raise UserError(f"You can not set Pre-Sale products to the pre_order.")

    @api.onchange('vendor_selection_strategy')
    def onchange_vendor_selection_strategy(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 07/01/25
            Task: Migration to v18 from v16
            Purpose : set vendor_id false if the selection strategy if other than specific vendor.
                    : strategy related changes as per the 16.
        """
        if self.vendor_selection_strategy != 'specific_vendor':
            value = {'value': {'vendor_id': False}, 'domain': {
                'product_ids': [('active', '!=', False), ('purchase_ok', '!=', False),
                                ('can_be_used_for_advance_reordering', '!=', False)]}}
        else:
            value = {}
        return value

    @api.depends('vendor_id')
    def _compute_products_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 07/01/25
            Task: Migration to v18 from v16
            Purpose: get products as per selected vendors or all if there is no vendor and also add the domain as per the 16..
        """
        company_ids = self.env.context.get('allowed_company_ids', [])
        for record in self:
            if record.vendor_id:
                products = self.env['product.supplierinfo'].sudo().search(
                    [('partner_id', '=', record.vendor_id.id)]).mapped('product_tmpl_id').mapped(
                    'product_variant_ids').filtered(lambda x: x.active != False and x.purchase_ok != False and (
                            x.company_id.id in company_ids or not x.company_id) and x.can_be_used_for_advance_reordering != False)
                record.products_ids = products if products else False
            else:
                products = self.env['product.product'].sudo().search([('active', '!=', False),
                                                                      ('purchase_ok', '!=', False),('can_be_used_for_advance_reordering', '!=', False),
                                                                      ('company_id','in',company_ids + [False])])
                record.products_ids = products if products else False
            # for product in record.product_ids:
            #     product.write({'reorder_planner_template_ids': [(4, record.id)]})
            #
            # all_products = self.env['product.product'].search([('reorder_planner_template_ids', 'in', record.ids)])
            # removed_products = all_products - record.product_ids
            # for removed_product in removed_products:
            #     removed_product.write({'reorder_planner_template_ids': [(3, record.id)]})

    def verify_reorder_planing(self):
        """
             added by: Aastha Vora | On: Oct - 16 - 2024 | Task: 998
             use: verify action button use to verify planning record.
        """
        if not self.product_ids or not self.config_ids:
            raise UserError('Please add warehouse group in configuration tab or select product')
        self.write({'state': 'verified'})
        return True

    def reset_to_draft(self):
        """
             added by: Aastha Vora | On: Oct - 16 - 2024 | Task: 998
             use: Reset to draft button action use to reset planning record to draft state.
        """
        self.write({'state': 'draft'})
        return True

    def get_vendor_product_mapping_dict(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 07/01/25
            Task: Migration to v18 from v16
            Purpose: get products as per the selected vendor and can_be_used_for_advance_reordering changes are added as per the 16.
        """
        if self.only_out_of_stock_product:
            warehouse_ids = self.config_ids.mapped('warehouse_group_id').mapped('warehouse_ids')
            query = """
                       Select product_id from get_products_outofstock_data('{}','%s','{}','%s','%s','%s', '%s') 
                       where out_of_stock_qty > 0 
                   """ % (set(self.product_ids.ids), set(warehouse_ids.ids),
                          datetime.today().date() - timedelta(days=self.past_days),
                          datetime.today().date(), self.buffer_security_days)

            self._cr.execute(query)
            product_ids = set([row[0] for row in self._cr.fetchall()])
            product_ids = self.env['product.product'].browse(product_ids)
        else:
            product_ids = self.product_ids.filtered(lambda x:x.can_be_used_for_advance_reordering)
        vendor_product_dict = {}
        if self.vendor_selection_strategy == 'specific_vendor':
            vendor_product_dict.update({self.vendor_id.id: self.product_ids.filtered(lambda x:x.can_be_used_for_advance_reordering and self.vendor_id.id in (x.seller_ids.partner_id.ids)).ids})
        else:
            for product_id in product_ids:
                vendor_id = product_id.with_context({'sory_by': self.vendor_selection_strategy,
                                                     'op_company': self.user_id.company_id})._select_seller(
                    quantity=None)

                if vendor_id.partner_id.id in vendor_product_dict.keys():
                    vendor_product_dict.get(vendor_id.partner_id.id).append(product_id.id)
                else:
                    vendor_product_dict.update({vendor_id.partner_id.id: product_id.ids})
        return vendor_product_dict

    def prepare_vales_for_reorder(self, vendor, product_list):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 07/01/25
            Task: Migration to v18 from v16
            Purpose: Prepare vals to create reorder record and also changes are made as per the 16 which is as 14.
        """
        vendor_id = self.env['res.partner'].browse(vendor)
        product_ids = self.env['product.product'].browse(product_list)
        config_vals = []
        vendor_lead = vendor_id.vendor_pricelist_ids.filtered(
            lambda x: x.product_id.id in product_list or x.product_tmpl_id in product_ids.mapped('product_tmpl_id'))
        calc_base_on = self.env['advance.reordering.settings'].search([]).vendor_lead_days_method
        lead_days = 0
        if calc_base_on == 'static':
            lead_days = self.env['advance.reordering.settings'].search([]).vendor_static_lead_days
        elif calc_base_on == 'max':
            if not vendor_lead:
                raise ValidationError(
                    _("Please ensure that the Vendor is specified in the 'Purchase' tab of all the products that are selected when creating a Reorder with Real Demand Planner."))
            lead_days = max(vendor_lead.mapped('delay'))
        elif calc_base_on == 'minimum':
            if not vendor_lead:
                raise ValidationError(
                    _("Please ensure that the Vendor is specified in the 'Purchase' tab of all the products that are selected when creating a Reorder with Real Demand Planner."))
            lead_days = min(vendor_lead.mapped('delay'))
        elif calc_base_on == 'avg':
            if not vendor_lead:
                raise ValidationError(
                    _("Please ensure that the Vendor is specified in the 'Purchase' tab of all the products that are selected when creating a Reorder with Real Demand Planner."))
            lead_days = mean(vendor_lead.mapped('delay'))
        for config_id in self.config_ids:
            if calc_base_on == 'static':
                lead_days = config_id.vendor_lead_days
            config_vals.append((0, 0, {'warehouse_group_id': config_id.warehouse_group_id.id,
                                       'default_warehouse_id': config_id.default_warehouse_id.id,
                                       'vendor_lead_days': lead_days or 1}))
        start_date = datetime.today().date() + timedelta(days=self.config_ids[0].vendor_lead_days) - timedelta(days=self.past_days)
        end_date = start_date + timedelta(days=self.buffer_security_days)
        vals = {'vendor_id': vendor_id.id,
                'user_id': self.user_id.id,
                'reorder_date': datetime.now(),
                'buffer_security_days': self.buffer_security_days,
                'generate_demand_with': self.generate_demand_with,
                'sales_start_date': start_date,
                'sales_end_date': end_date,
                'reorder_demand_growth': self.reorder_demand_growth,
                'volume_uom_name': self.env['advance.reorder.orderprocess']._default_volume_uom_name(),
                'reorder_planner_id': self.id,
                'product_ids': [(6, 0, product_ids.ids)],
                'config_ids': config_vals,
                'purchase_order_type': self.purchase_order_type
                }
        return vals

    def create_real_demand_record(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 07/01/25
            Task: Migration to v18 from v16
            Purpose: Run Manually button action use to create Real Demand Record, also made changes as per the 16 which is as per 14 vendor_id condition added.

            Author: nidhi@setconsulting.com,  Date: 22/08/25
            Task : AR's Issue {https://app.clickup.com/t/86dxehbn6}
            modified : remove code that updating draft record instead of creating new record [in-short revert changes as version 16 ]
        """
        real_demand_obj = self.env['advance.reorder.orderprocess']
        vendor_product_dict = self.get_vendor_product_mapping_dict()
        for vendor_id, product_ids in vendor_product_dict.items():
            if vendor_id:
                vals = self.prepare_vales_for_reorder(vendor_id, product_ids)
                rec = real_demand_obj.create(vals)
                for x in rec.config_ids:
                    x.onchange_vendor_lead_days()
                    x.onchange_order_arrival_date()

                if self.auto_workflow_id.validate:
                    rec.action_reorder_confirm()
                if self.auto_workflow_id.verify:
                    rec.action_reorder_verified()
                if self.state == 'verified':
                    if self.auto_workflow_id.create_po:
                        rec.action_create_reorder_purchase_order()
                    if self.auto_workflow_id.create_replenishment:
                        rec.create_warehouse_replenishment()
                    if self.auto_workflow_id.validate_replenishment:
                        for replenishment in rec.replenishment_ids:
                            replenishment.action_procurement_confirm()

                self.write({'previous_execution_date': datetime.today().date(),
                            'next_execution_date': datetime.today().date() + timedelta(days=self.planing_frequency)
                            })

        return True

    def auto_create_real_demand_record(self):
        """
             added by: Aastha Vora | On: Oct - 16 - 2024 | Task: 998
             use: auto create real demand record.
        """
        records = self.search([('next_execution_date', '<=', datetime.today().date()), ('state', '=', 'verified')])
        for record in records:
            record.create_real_demand_record()
        return True

    def action_reorder_count(self):
        """
             added by: Aastha Vora | On: Oct - 16 - 2024 | Task: 998
             use: Is an Reorder Smart Button action used get Reorder records.
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_advance_reordering.actions_advance_reorder_orderprocess")
        reorder = self.mapped('reorder_ids')
        if len(reorder) > 1:
            action['domain'] = [('id', 'in', reorder.ids)]
        elif reorder:
            form_view = [(self.env.ref('setu_advance_reordering.form_advance_reorder_orderprocess').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = reorder.id
        return action

    def action_purchase_count(self):
        """
               added by: Aastha Vora | On: Oct - 16 - 2024 | Task: 998
               use: Is an purchase order smart button action used get purchase order records.
        """
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")

        purchases = self.mapped('purchase_ids')
        if len(purchases) > 1:
            action['domain'] = [('id', 'in', purchases.ids)]
        elif purchases:
            form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = purchases.id
        return action

