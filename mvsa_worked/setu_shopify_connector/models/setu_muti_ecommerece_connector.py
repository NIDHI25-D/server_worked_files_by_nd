from datetime import datetime, timedelta

import pytz
from dateutil import parser
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

utc = pytz.utc
from .. import shopify


class SetuMultiEcommerceConnector(models.Model):
    _inherit = 'setu.multi.ecommerce.connector'

    @api.model
    def _get_set_order_status(self):
        shopify_order_status_ids = self.env['setu.shopify.order.status'].search([])
        if shopify_order_status_ids:
            return [(6, 0, [shopify_order_status_ids[0].id])]
        else:
            return False

    def _get_set_shopify_order_from(self):
        sale_order_obj = self.env["sale.order"]
        order_after_date = datetime.now() - timedelta(30)
        if not self.import_shopify_order_from:
            if (order_id := sale_order_obj.search([('multi_ecommerce_connector_id', '=', self.id)],
                                                  order='date_order asc', limit=1) or False):
                order_after_date = order_id.date_order
            else:
                order_after_date = datetime.now() - timedelta(30)
            self.write({"import_shopify_order_from": order_after_date})

        return order_after_date

    ecommerce_connector = fields.Selection(selection_add=[('shopify_connector', 'Shopify')],
                                           default='shopify_connector', string="e-Commerce Connector",
                                           ondelete={'shopify_connector': 'set default'})

    # Store Setup
    shopify_api_key = fields.Char(string="API Key")
    shopify_password = fields.Char(string="API Access Token")
    shopify_shared_secret = fields.Char(string="Secret Key")
    shopify_host = fields.Char(string="Shopify Host")
    shopify_store_time_zone = fields.Char(string="Store Time Zone")
    version_control = fields.Selection([
        ('2024-10', '2024-10'),
        ('2024-01', '2024-01'),
        ('2024-04', '2024-04'),
        ('2024-07', '2024-07')
    ], string="Shopify Version Control", default='2024-10')

    # Shopify Setup - product configuration
    is_sync_shopify_product_images = fields.Boolean(string="Sync Shopify Images", default=True)
    is_auto_fulfill_gift_card_order = fields.Boolean(string="Automatically fulfill only the gift cards of the order",
                                                     default=True)
    is_auto_import_shopify_cost = fields.Boolean(string="Is Auto Import Shopify Cost", default=False,
                                                 help="This option is only manage the Auto Create Product if the new product is create in odoo then it will be update.")
    is_auto_assigned_category_configuration = fields.Boolean(string="Is Auto Assigned Category Configuration",
                                                             default=False,
                                                             help="This option is only manage the create new category with the Costing Method and Inventory Valuation.")
    shopify_mapped_with_odoo_product = fields.Selection(
        [('default_code', 'Internal Reference(Default Code)'), ('barcode', 'Barcode'),
         ('default_code_or_barcode', 'Internal Reference or Barcode')], string="Product Search Pattern",
        default='default_code')
    property_cost_method = fields.Selection([('standard', 'Standard Price'),
                                             ('fifo', 'First In First Out (FIFO)'),
                                             ('average', 'Average Cost (AVCO)')], string="Costing Method",
                                            company_dependent=True, copy=True,
                                            help="""Standard Price: The products are valued at their standard cost defined on the product.
                    Average Cost (AVCO): The products are valued at weighted average cost.
                    First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
                    """)
    property_valuation = fields.Selection([('manual_periodic', 'Manual'),
                                           ('real_time', 'Automated')], string='Inventory Valuation',
                                          company_dependent=True, copy=True,
                                          help="""Manual: The accounting entries to value the inventory are not posted automatically.
                  Automated: An accounting entry is automatically created to value the inventory when a product enters or leaves the company.
                  """)

    # Shopify Setup - order configuration
    shopify_order_status_ids = fields.Many2many('setu.shopify.order.status',
                                                'setu_shopify_ecommerce_connector_order_status_rel',
                                                'multi_ecommerce_connector_id', 'shopify_order_status_id',
                                                "Shopify Order Status", default=_get_set_order_status)
    shopify_default_pos_customer_id = fields.Many2one("res.partner", string="Default POS customer")
    import_shopify_order_from = fields.Datetime(string="Import Shopify Order From", default=_get_set_shopify_order_from)

    # Shopify Setup - payout report configuration
    shopify_settlement_report_journal_id = fields.Many2one('account.journal', string='Payout Report Journal')
    shopify_payment_account_configuration_ids = fields.One2many("setu.shopify.payment.account.configuration",
                                                                "multi_ecommerce_connector_id",
                                                                string="Payout Configuration Line")

    # Shopify Setup - order process setup
    shopify_sale_order_process_ids = fields.One2many('setu.shopify.sale.order.process.configuration',
                                                     'multi_ecommerce_connector_id',
                                                     string="Order Process Configuration")

    # Shopify Setup - webhook setup
    shopify_webhook_ids = fields.One2many("setu.shopify.webhook", "multi_ecommerce_connector_id",
                                          string="Shopify Webhooks")

    is_use_odoo_order_prefix = fields.Boolean(string="Use Odoo Order Prefix", default=True)

    shopify_last_product_import = fields.Datetime(string="Last Date Product Import")
    last_unshipped_order_import = fields.Datetime(string="Last Date of Unshipped Order Import")
    last_shipped_order_import = fields.Datetime(string="Last Date Of Shipped Order Import")
    shopify_last_update_product_stock = fields.Datetime(string="Shopify Last Product Stock Export")
    shopify_last_customer_import = fields.Datetime(string="Shopify Last Date Customer Import")
    last_payment_report_import = fields.Date(string="Last Date Payment Report Import")

    shopify_shop_api_url = fields.Char(string="Shopify Shop API URL")

    shopify_payment_gateway_ids = fields.One2many('setu.shopify.payment.gateway', 'multi_ecommerce_connector_id',
                                                  string="Shopify Payment Gateway")
    shopify_product_count = fields.Integer(compute='_get_number_of_multi_connector_count',
                                           string="Shopify Product Count")
    shopify_sale_order_count = fields.Integer(compute='_get_number_of_multi_connector_count',
                                              string="Shopify Sale Order Count")
    shopify_account_move_count = fields.Integer(compute='_get_number_of_multi_connector_count',
                                                string="Shopify Customer Invoice")
    setu_shopify_product_template_ids = fields.One2many('setu.shopify.product.template', 'multi_ecommerce_connector_id',
                                                        string="Products")
    shopify_sale_order_ids = fields.One2many('sale.order', 'multi_ecommerce_connector_id', string="Shopify Sale Orders")

    picking_ids = fields.One2many('stock.picking', 'multi_ecommerce_connector_id', string="Pickings")
    picking_count = fields.Integer(compute='_get_number_of_multi_connector_count', string="Picking")

    account_move_ids = fields.One2many('account.move', 'multi_ecommerce_connector_id',
                                       string="Shopify Customer Invoices")

    customer_ids = fields.One2many('res.partner', 'multi_ecommerce_connector_id', string="Customers")
    customer_count = fields.Integer(compute='_get_number_of_multi_connector_count', string="Customers Count")

    payment_gateway_count = fields.Integer(compute='_get_number_of_multi_connector_count', string="Payment Count")

    shopify_location_ids = fields.One2many('setu.shopify.stock.location', 'multi_ecommerce_connector_id',
                                           string="Shopify Location")
    shopify_location_count = fields.Integer(compute='_get_number_of_multi_connector_count', string="Location Count")

    def _get_number_of_multi_connector_count(self):
        for record_id in self:
            record_id.shopify_product_count = len(record_id.setu_shopify_product_template_ids)
            record_id.shopify_sale_order_count = len(record_id.shopify_sale_order_ids)
            record_id.picking_count = len(record_id.picking_ids)
            record_id.shopify_account_move_count = len(record_id.account_move_ids)
            record_id.customer_count = len(record_id.customer_ids)
            record_id.payment_gateway_count = len(record_id.shopify_payment_gateway_ids)
            record_id.shopify_location_count = len(record_id.shopify_location_ids)

    def action_sale_order_count(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "setu_shopify_connector.setu_multi_ecommerce_connector_sale_action"
        )

    def action_account_move_account(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "setu_shopify_connector.setu_shopify_account_move_commerce_invoice_action"
        )

    def action_product_count(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "setu_shopify_connector.setu_multi_ecommerce_connector_template_action"
        )
