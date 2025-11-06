from odoo import fields, models, api, _
from datetime import datetime, timedelta, date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_consume_loyalty_points = fields.Boolean(help="""This permission is so that all
            the contact's purchases are accumulated in the master company and the contact can
            use the loyalty points of said company.""", string="Consume the global points of the master company",
                                               default=True)

    is_budgets_permission = fields.Boolean(help="""This permission allows you to view budgets.""", string="Budgets",
                                           default=True)
    is_sale_orders_permission = fields.Boolean(help="""This permission allows you to view sales orders.""",
                                               string="Sale Orders", default=True)
    is_purchase_permission = fields.Boolean(help="""This permission allows you to view purchase orders.""",
                                            string="Purchase Orders", default=True)
    is_invoices_permission = fields.Boolean(help="""This permission allows you to view invoices.""", string="Invoices",
                                            default=True)
    is_claims_permission = fields.Boolean(help="""This permission is for filing claims.""", string="Claims",
                                          default=True)
    is_main_partner = fields.Boolean(string="Is Main Partner")
    is_owner = fields.Boolean(string="Is Owner")
    is_required_invoice = fields.Boolean(string="Is Required an invoice")
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    is_company_data = fields.Boolean(string="Is Company Data")
    requested_company_id = fields.Many2one('res.partner')
    setu_company_type = fields.Selection(
        selection=[
            ('legal', 'Legal'),
            ('pisical', 'Pisical'),
        ], string='Company Type')
    is_company_user = fields.Boolean(string="Is Company User")

    def get_permission_status(self,url):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: return whether the true or false as per the field for URL.
        """
        if url == '/my/quotes':
            return self.env.user.partner_id.is_budgets_permission
        if url == '/my/orders':
            return self.env.user.partner_id.is_sale_orders_permission
        if url == '/my/claims':
            return self.env.user.partner_id.is_claims_permission
        if url == '/my/purchase':
            return self.env.user.partner_id.is_purchase_permission
        if url == '/my/rfq':
            return self.env.user.partner_id.is_purchase_permission
        # if url == '/my/invoices?filterby=invoices' or url == '/my/invoices?filterby=bills':
        if '/my/invoices' in url:  # as per the default odoo changes we have takes this change to shows invoices related button in portal
            return self.env.user.partner_id.is_invoices_permission
        if url == '/my/contacts':
            return True

    def check_contacts(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: execute scheduled action for contacts --> after seven business days if not sale order are created and category is RAM so deleted partners and corresponding to it's user if exists.
        """
        ir_config_parameter_obj = self.env['ir.config_parameter'].sudo()
        ram_hcategory_id = ir_config_parameter_obj.get_param(
            'setu_ecommerce_checkout_extended.ram_hcategory_id')
        partners_to_consider_after_date = ir_config_parameter_obj.get_param(
            'setu_ecommerce_checkout_extended.partners_to_consider_after_date')
        if not (partners_to_consider_after_date and ram_hcategory_id):
            return True
        convert_to_datetime = datetime.strptime(partners_to_consider_after_date, "%Y-%m-%d %H:%M:%S")
        today = datetime.now().date()
        seven_working_days = fields.Datetime.from_string(today)
        date_to_calculate = fields.Datetime.from_string(today)
        days_to_add = 7
        while days_to_add > 0:
            date_to_calculate -= timedelta(days=1)
            if date_to_calculate.weekday() < 5:
                days_to_add -= 1
                seven_working_days = date_to_calculate

        partner_ids = self.search([('hcategory_id', '=', int(ram_hcategory_id)), ('create_date', '<', seven_working_days), ('create_date', '>', convert_to_datetime)])

        for partner_id in partner_ids:
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner_id.id), ('create_date', '>=', seven_working_days), ('create_date', '<=', datetime.now())])
            if sale_orders:
                continue
            if partner_id and partner_id.user_ids:
                partner_id.user_ids.write({'active': False})
                partner_id.write({'active': False})

            else:
                partner_id.write({'active': False})


