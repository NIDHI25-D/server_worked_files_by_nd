# -*- coding: utf-8 -*-
import logging
from calendar import monthrange
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

_secondsConverter = {
    'days': lambda interval: interval * 24 * 60 * 60,
    'hours': lambda interval: interval * 60 * 60,
    'weeks': lambda interval: interval * 7 * 24 * 60 * 60,
    'minutes': lambda interval: interval * 60,
}


class SetuMultiEcommerceConnector(models.Model):
    _name = "setu.multi.ecommerce.connector"
    _description = "Multi e-Commerce Connector"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_set_default_warehouse(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default warehouse based on company
        :return: warehouse_id
        """
        stock_warehouse_obj = self.env['stock.warehouse']
        warehouse_id = stock_warehouse_obj.search([('company_id', '=', self.odoo_company_id.id)], limit=1, order='id')
        return warehouse_id.id if warehouse_id else False

    @api.model
    def _get_set_default_gift_product(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default gift product
        :return: gift_product_id
        """
        gift_product_id = self.env.ref('setu_ecommerce_based.setu_ecommerce_gift_card_product', False)
        return gift_product_id

    @api.model
    def _get_set_default_ship_product(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default ship product
        :return: ship_product_id
        """
        ship_product_id = self.env.ref('setu_ecommerce_based.setu_ecommerce_shipping_product', False)
        return ship_product_id

    @api.model
    def _get_set_default_discount_product(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default discount product
        :return: discount_product_id
        """
        discount_product_id = self.env.ref('setu_ecommerce_based.setu_ecommerce_discount_product', False)
        return discount_product_id

    @api.model
    def _default_custom_service_product(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default service product
        :return:
        """
        custom_service_product = self.env.ref('setu_ecommerce_based.setu_ecommerce_custom_product', False)
        return custom_service_product

    @api.model
    def _default_custom_storable_product(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default custom storable product
        :return: custom_storable_product
        """
        custom_storable_product = self.env.ref('setu_ecommerce_based.setu_ecommerce_custom_storable_product', False)
        return custom_storable_product

    @api.model
    def _default_language(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default user language
        :return: language id
        """
        lang_code = self.env.user.lang
        language = self.env["res.lang"].search([('code', '=', lang_code)])
        return language.id if language else False

    @api.model
    def _default_stock_field(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : Set default stock field
        :return: stock field id
        """
        stock_field = self.env['ir.model.fields'].search([
            ('model_id.model', '=', 'product.product'), ('name', '=', 'free_qty')], limit=1)
        return stock_field.id if stock_field else False

    # Conditional fields
    active = fields.Boolean(default=True, string="Active")
    is_auto_create_product = fields.Boolean(string="Auto Create Product")
    is_use_odoo_order_prefix = fields.Boolean(string="Use Odoo Order Prefix", default=True)
    is_use_default_product_description = fields.Boolean(string="Use Default Product Description")
    is_auto_validate_inventory = fields.Boolean(string="Auto Validate Inventory")

    # Integer or Float fields
    color = fields.Integer(string='Color Index', default=0, help='Used to decorate kanban view')

    # Image fields
    image = fields.Image(max_width=256, max_height=256, string="Image")

    # Char fields
    name = fields.Char(string="e-Commerce Connector Name", required=True, translate=True)
    order_prefix = fields.Char(size=10, string="Order Prefix", help="Enter your order prefix")

    # Selection fields
    state = fields.Selection(
        selection=[('draft', "Draft"), ('integrated', 'Integrated'),
                   ('fully_integrated', 'Fully Integrated'), ('error', 'Error')],
        string="State", default='draft')
    ecommerce_connector = fields.Selection(
        selection=[('none', "No e-Commerce Set")],
        default='none', required=True)
    order_odoo_tax_behavior = fields.Selection(
        selection=[("follow_e_commerce_tax_create_odoo", "Follow e-Commerce Tax-(Create New Tax in Odoo If not Found)"),
                   ("follow_odoo_tax", "Follow Odoo Tax")],
        default='follow_odoo_tax', copy=False, string="Order Tax Behavior")

    # Relational fields
    odoo_company_id = fields.Many2one(
        comodel_name="res.company", string="Company", required=True,
        default=lambda self: self.env.user.company_id)
    odoo_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", string="Warehouse",
        default=_get_set_default_warehouse,
        domain="[('company_id', '=',odoo_company_id)]")
    odoo_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist", string="Pricelist")
    stock_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Stock Field", default=_default_stock_field)
    crm_team_id = fields.Many2one(
        comodel_name="crm.team", string="Sales Team")
    odoo_lang_id = fields.Many2one(
        comodel_name="res.lang",
        string="Language", default=_default_language)
    odoo_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency", help="Multi-Commerce Currency.",
        default=lambda self: self.env.user.company_id.currency_id.id)
    default_invoice_tax_account_id = fields.Many2one(
        comodel_name="account.account", string="Invoice Tax Account")
    default_credit_tax_account_id = fields.Many2one(
        comodel_name="account.account", string="Credit Tax Account")
    discount_product_id = fields.Many2one(
        comodel_name="product.product", string="Discount Product",
        domain=[('type', '=', 'service')], default=_get_set_default_discount_product)
    gift_product_id = fields.Many2one(
        comodel_name="product.product", string="Gift Product",
        domain=[('type', '=', 'service')], default=_get_set_default_gift_product)
    shipping_product_id = fields.Many2one(
        comodel_name="product.product", string="Shipping Product",
        domain=[('type', '=', 'service')], default=_get_set_default_ship_product)
    custom_service_product_id = fields.Many2one(
        comodel_name="product.product", string="Custom Service Product",
        domain=[('type', '=', 'service')],
        default=_default_custom_service_product)
    custom_storable_product_id = fields.Many2one(
        comodel_name="product.product", string="Custom Storable Product",
        domain=[('type', '=', 'consu'), ('is_storable', '=', True)],
        default=_default_custom_storable_product)

    def _compute_display_name(self):
        for rec in self:
            connector = dict(rec._fields['ecommerce_connector'].selection).get(rec.ecommerce_connector)
            rec.display_name = f"{rec.name} ({connector})"

    # @api.model
    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         connector = dict(rec._fields['ecommerce_connector'].selection).get(rec.ecommerce_connector)
    #         name = rec.name
    #         res.append((rec.id, '%s (%s)' % (name, connector)))
    #     return res

    def test_ecommerce_connection_action(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use for connection ecommerce connector
        :return: None
        """
        self.ensure_one()
        if hasattr(self, 'connection_%s' % self.ecommerce_connector):
            res, msg = getattr(self, 'connection_%s' % self.ecommerce_connector)()
            if res:
                self.state = 'integrated'
            else:
                self.state = 'error'
        elif hasattr(self, 'test_%s_connection' % self.ecommerce_connector):
            return getattr(self, 'test_%s_connection' % self.ecommerce_connector)()
        else:
            return self.display_message('Connection protocol missing.')

    def display_message(self, message):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use for display connection message
        :param message:
        :return: wizard with connector connection message
        """
        return self.env['setu.display.message.wiz'].generated_message(message, 'Summary')

    def cron_configuration_action(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to cron configuration for ecommerce connector
        :return: action
        """
        action = self.env.ref('setu_ecommerce_based.setu_cron_configuration_wiz_action').sudo().read()[0]
        action['context'] = {'multi_ecommerce_connector_id': self.id}
        return action

    def reset_ecommerce_connection_action(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to change state of ecommerce connector
        :return:
        """
        self.state = 'draft'

    def get_cron_execution_time(self, cron_name):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to get cron execution time
        :param cron_name:
        :return:
        """
        process_chain_cron = self.env.ref(cron_name, False)

        if not process_chain_cron:
            raise ValidationError(
                _("Please upgrade the module.Maybe the job has been deleted, "
                  "it will be recreated at the time of module upgrade."))

        interval = process_chain_cron.interval_number
        interval_type = process_chain_cron.interval_type

        if interval_type == "months":
            days = 0
            current_year = fields.Date.today().year
            current_month = fields.Date.today().month
            for i in range(0, interval):
                month = current_month + i

                if month > 12:
                    if month == 13:
                        current_year += 1
                    month -= 12

                days_in_month = monthrange(current_year, month)[1]
                days += days_in_month

            interval_type = "days"
            interval = days
        interval_in_seconds = _secondsConverter[interval_type](interval)
        return interval_in_seconds

    def toggle_active_value(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to disable instance
        :return: True
        """
        if hasattr(self, '%s_toggle_active_value' % self.ecommerce_connector):
            getattr(self, '%s_toggle_active_value' % self.ecommerce_connector)()
        return True

    def fully_integrate(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use for fully integrate ecommerce connector
        :return: True
        """
        if hasattr(self, '%s_fully_integrate' % self.ecommerce_connector):
            getattr(self, '%s_fully_integrate' % self.ecommerce_connector)()
        return True


    def get_or_create_pricelist(self, shop_currency):
        res_currency_obj = self.env["res.currency"]
        product_pricelist_obj = self.env["product.pricelist"]

        currency_id = res_currency_obj.search([("name", "=", shop_currency)], limit=1)

        if not currency_id:
            currency_id = res_currency_obj.with_context(active_test=False).search([("name", "=", shop_currency)],
                                                                                  limit=1)
            if currency_id:
                currency_id.write({"active": True})
        if not currency_id:
            currency_id = self.env.user.currency_id

        price_list_name = f"{self.name} Price List"
        pricelist_id = product_pricelist_obj.search(
            [("name", "=", price_list_name), ("currency_id", "=", currency_id.id),
             ("company_id", "=", self.odoo_company_id.id)], limit=1)
        if not pricelist_id:
            pricelist_id = product_pricelist_obj.create(
                {"name": price_list_name, "currency_id": currency_id.id, "company_id": self.odoo_company_id.id})

        return pricelist_id
