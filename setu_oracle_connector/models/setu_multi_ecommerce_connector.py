from odoo.exceptions import ValidationError

from odoo import fields, models, _, SUPERUSER_ID, api
# from .import_method import GetToken
from datetime import datetime, timedelta


class SetuMultiEcommerceConnector(models.Model):
    _inherit = 'setu.multi.ecommerce.connector'

    oracle_connector_name = fields.Char(string='Connector Name:')
    user_name = fields.Char(string='User name or email address')
    password = fields.Char(string='Password')
    oracle_authorization = fields.Text(string='Token', readonly=True)
    host = fields.Char(string='Host')
    remember_client = fields.Boolean(string='Remember client')
    company_id = fields.Many2one('res.company', string='Company')
    ecommerce_connector = fields.Selection(selection_add=[('oracle_connector', 'Oracle')], default='oracle_connector',
                                           ondelete={'oracle_connector': 'set default'})
    vendor = fields.Char(string='Vendor Id')
    private_key = fields.Char(string='Private Key')

    oracle_stock_pick_type = fields.Selection([('all', 'All'),
                                               ('specific', 'Specific'),
                                               ('several', 'Several')],
                                              string="Default Stock Location", default="all")
    stock_location_id = fields.Many2one("stock.location", string="Stock Location")
    stock_location_ids = fields.Many2many("stock.location", string="Stock Locations")
    stock_percentage = fields.Integer(string='Stock Percentage To Consider')
    minimum_stock_quantities = fields.Integer()
    oracle_mapped_with_odoo_product = fields.Selection(
        [('default_code', 'Internal Reference(Default Code)'), ('barcode', 'Barcode'),
         ('default_code_or_barcode', 'Internal Reference or Barcode')], string="Product Search Pattern",
        default='default_code')
    setu_oracle_product_template_ids = fields.One2many('setu.oracle.product.template', 'multi_ecommerce_connector_id',
                                                       string="Products")
    oracle_sale_order_ids = fields.One2many('sale.order', 'multi_ecommerce_connector_id', string="Oracle Sale Orders")
    oracle_invoice_ids = fields.One2many('account.move', 'multi_ecommerce_connector_id', string="Oracle Invoices")
    oracle_product_count = fields.Integer(compute="_get_number_of_products_count", string="Oracle Product Count")
    oracle_sale_order_count = fields.Integer(compute="_get_number_of_products_count", string="Oracle Order Count")
    # oracle_invoice_count = fields.Integer(compute="_get_number_of_products_count", string="Oracle Invoice Count")
    oracle_partner_id = fields.Many2one('res.partner', string='Set Partner for Orders')

    # def _get_number_of_products_count(self):
    #     for record_id in self:
    #         record_id.oracle_product_count = len(record_id.setu_oracle_product_template_ids)
    #         record_id.oracle_sale_order_count = len(record_id.oracle_sale_order_ids)
    #         # record_id.oracle_invoice_count = len(record_id.oracle_sale_order_ids)
    #
    # @api.constrains('user_name', 'host')
    # def _check_username_password(self):
    #     for rec in self:
    #         exists = self.search([('host', '=', rec.host), ('user_name', '=', rec.user_name), ('id','!=',rec.id),('ecommerce_connector','=','oracle_connector')])
    #         if len(exists) > 1:
    #             raise ValidationError(_("Username %s Already Exists" % rec.user_name))
    #         else:
    #             return True
    #
    # def connection_oracle_connector(self):
    #     url = self.host
    #     payload = {
    #         'userNameOrEmailAddress': self.user_name,
    #         'password': self.password,
    #         "rememberClient": self.remember_client
    #     }
    #     headers = {
    #         'Content-Type': 'application/json'
    #     }
    #     token = GetToken(url, payload, headers)
    #     response = token.get_token()
    #     if response.status_code == 200:
    #         result = response.json()
    #         access_token = result.get('result')['accessToken']
    #         if access_token:
    #             self.oracle_authorization = access_token
    #             return True, 'Successfully'
    #     else:
    #         return False, "Unsuccessful"
    #
    # def check_core_cron(self, name):
    #     try:
    #         core_cron = self.env.ref(name)
    #     except:
    #         core_cron = False
    #     if not core_cron:
    #         raise ValidationError(
    #             _('Core settings of e-Commerce are deleted, Please upgrade the e-Commerce Base Module to back these settings.'))
    #     return core_cron
    #
    # def create_ir_module_data(self, module, name, new_cron):
    #     self.env['ir.model.data'].create(
    #         {'module': module, 'name': name, 'model': 'ir.cron', 'res_id': new_cron.id, 'noupdate': True})
    #
    # def oracle_connector_fully_integrate(self):
    #     if not (self.odoo_company_id or self.odoo_warehouse_id or self.stock_field_id or self.odoo_pricelist_id):
    #         raise ValidationError(_('Please select a company'))
    #     if not self.oracle_authorization:
    #         raise ValidationError(_('User is not authorized'))
    #     self.state = 'fully_integrated'
    #     self.scheduled_actions_for_token()
    #
    # def cron_auto_update_token_in_oracle(self, ctx):
    #     if ctx.get('multi_ecommerce_connector_id'):
    #         self = self.env['setu.multi.ecommerce.connector'].browse(ctx.get('multi_ecommerce_connector_id'))
    #         self.connection_oracle_connector()
    #     return True
    #
    # def scheduled_actions_for_token(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 08/08/23
    #         Task: Oracle API - Phase 1
    #         Purpose: Create cron for login every 23 hours.
    #     """
    #     if self.state == 'fully_integrated':
    #         # current_time = datetime.now()
    #         vals = {
    #             'active': True,
    #             'interval_number': 23,
    #             'interval_type': 'hours',
    #             'user_id': SUPERUSER_ID,
    #             'nextcall': datetime.now() + timedelta(hours=23),
    #             'code': "model.cron_auto_update_token_in_oracle(ctx={'multi_ecommerce_connector_id':%d})" % self.id
    #         }
    #
    #         core_cron = self.check_core_cron("setu_oracle_connector.cron_action_token")
    #         name = self.name + " : " + dict(
    #             self._fields['ecommerce_connector'].selection).get(
    #             self.ecommerce_connector) + ' : ' + core_cron.name
    #         vals.update({'name': name})
    #         new_cron = core_cron.copy(default=vals)
    #         name = 'ir_cron_oracle_auto_update_token_ecommerce_connector_%d' % self.id
    #         module = 'setu_oracle_connector'
    #         self.create_ir_module_data(module, name, new_cron)
    #     return True
    #
    # def reset_ecommerce_connection_action(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 08/08/23
    #         Task: Oracle API - Phase 1
    #         Purpose: Reset the connection.
    #     """
    #     res = super(SetuMultiEcommerceConnector, self).reset_ecommerce_connection_action()
    #     delete_crons = self.env['ir.cron'].search([('name', 'like',
    #                                                 self.name + " : " + dict(
    #                                                     self._fields['ecommerce_connector'].selection).get(
    #                                                     self.ecommerce_connector))])
    #     if delete_crons:
    #         delete_crons.unlink()
    #     return res
    #
    # def _get_oracle_location_type(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 08/08/23
    #         Task: Oracle API - Phase 1
    #         Purpose: Get the oracle stock pick type for export the stock.
    #     """
    #     conf_locations = []
    #     self = self.with_user(SUPERUSER_ID)
    #     if self.oracle_stock_pick_type == 'specific':
    #         conf_locations = (self.stock_location_id.ids if self.stock_location_id else [])
    #     elif self.oracle_stock_pick_type == 'several':
    #         conf_locations = (self.stock_location_ids.ids if self.stock_location_ids else [])
    #     elif self.oracle_stock_pick_type == 'all':
    #         conf_locations = (self.env['stock.location'].search([]).ids)
    #     return conf_locations
    #
    # def oracle_connector_toggle_active_value(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 08/08/23
    #         Task: Oracle API - Phase 1
    #         Purpose: Deactivate the particular oracle connector.
    #     """
    #     setu_auto_delete_process_obj = self.env['setu.auto.delete.process']
    #     domain = [("multi_ecommerce_connector_id", "=", self.id)]
    #     if self.active:
    #         active = {"active": False}
    #         self.write(active)
    #         self.oracle_authorization = False
    #         self.deactivate_active_cron()
    #         self.state = 'draft'
    #         setu_auto_delete_process_obj.auto_delete_process(is_delete_chain_process=True)
    #     else:
    #         self.connection_oracle_connector()
    #         active = {"active": True}
    #         domain.append(("active", "=", False))
    #         self.write(active)
    #     return True
    #
    # def deactivate_active_cron(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 08/08/23
    #         Task: Oracle API - Phase 1
    #         Purpose: Click on Active button for deactivate the cron related to particular connector.
    #     """
    #     try:
    #         ir_stock_cron_id = self.env.ref(
    #             'setu_oracle_connector.%d' % self.id)
    #     except:
    #         ir_stock_cron_id = False
    #     try:
    #         ir_login_cron_id = self.env.ref(
    #             'setu_oracle_connector.ir_cron_oracle_auto_update_token_ecommerce_connector_' % self.id)
    #     except:
    #         ir_login_cron_id = False
    #     if ir_stock_cron_id:
    #         ir_stock_cron_id.write({'active': False})
    #     if ir_login_cron_id:
    #         ir_login_cron_id.write({'active': False})
    #
    # def action_oracle_product_count(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "setu_oracle_connector.setu_oracle_product_template_main_action")
    #     return action
    #
    # def action_oracle_sale_order_count(self):
    #     action = self.env['ir.actions.actions']._for_xml_id(
    #         "setu_oracle_connector.setu_multi_ecommerce_connector_sale_action")
    #     return action
    #
    # # def action_oracle_invoice_count(self):
    # #     # Invoice Creation action is Remaining.
    # #     action = self.env['ir.actions.actions']._for_xml_id(
    # #         "setu_oracle_connector.setu_multi_ecommerce_connector_sale_action")
    # #     return action
    #
    # def cron_configuration_action(self):
    #     if self.ecommerce_connector != 'oracle_connector':
    #         return super().cron_configuration_action()
    #     else:
    #         # res = super().cron_configuration_action()
    #         action = self.env.ref('setu_oracle_connector.setu_oracle_cron_configuration_wiz_action').sudo().read()[0]
    #         action['context'] = {'multi_ecommerce_connector_id': self.id}
    #         return action
