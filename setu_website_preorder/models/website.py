from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo import models
from odoo.http import request
import logging
import pandas

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    stock_pick_type = fields.Selection([('All', 'All'),
                                        ('Specific', 'Specific'),
                                        ('Several', 'Several')],
                                       string="Default Stock Location", default="All")
    default_stock_location = fields.Many2one("stock.location",
                                             string="Stock Location",
                                             domain="[('usage', '=', 'internal')]")
    default_stock_location_ids = fields.Many2many("stock.location",
                                                  'website_sale_stock_configuration_stock_location_rel',
                                                  'website_sale_stock_config_id', 'location_id',
                                                  string="Stock Locations",
                                                  domain="[('usage', '=', 'internal')]")
    quantity_type = fields.Selection([('on_hand', 'Quantity On Hand'),
                                      ('forecast', 'Forecasted'),
                                      ('on_hand_outgoing', 'Quantity On Hand - Outgoing')],
                                     string="Stock Out Type", default="on_hand_outgoing")
    display_quantity = fields.Boolean(string="Display Product Quantity On Website")
    enable_pre_order = fields.Boolean(string='Enable PreOrder ', default=False)
    enable_pre_sale = fields.Boolean(string='Enable PreSale ', default=False)
    warehouse_id = fields.Many2one("stock.warehouse", string="Default Warehouse")
    warehouse_default_id = fields.Many2one("stock.warehouse", string="Default Warehouse")
    warehouse_default_ids = fields.Many2many("stock.warehouse", 'website_sale_warehouse_rel',
                                             string="Default Warehouses")
    presale_exchange_rate = fields.Float(string="Presale Exchange Rate")
    presale_pricelist = fields.Many2one("product.pricelist", string="Presale Pricelist")
    excluded_pricelist_id = fields.Many2one("product.pricelist", string="Excluded Pricelist")
    cash_payment = fields.Float(string="Cash Payment", default=1)
    available_qty_multiplier = fields.Integer(string="Available Quantity Multiplier")
    minimum_amt_qty = fields.Integer(string="Minimum Amount Quantity")
    days_for_calculation = fields.Integer(string="Configure Days for Website Available Quantity")
    international_preorder_msg = fields.Html(string="International Preorder Message", translate=True)
    intl_preorder_pricelist_id = fields.Many2one("product.pricelist", string="International Preorder Pricelist")
    cash_next_day_pricelist_id = fields.Many2one("product.pricelist", string="Cash Next Day Specific Pricelist")
    credit_next_day_pricelist_id = fields.Many2one("product.pricelist", string="Credit Next Day Specific Pricelist")
    presale_msg = fields.Html(string="Presale Message", translate=True, sanitize=False)
    activity_owner_ids = fields.Many2many('res.users', 'setu_website_preorder_users_rel', 'settings_id', 'user_id',
                                          string="Activity User", domain="[('share', '=', False)]")
    config_quantity = fields.Float(string="Config Quantity")
    enable_cancellation_sale_order = fields.Boolean(string="Enable Website sale orders cancellation", default=False)
    time_limit_to_cancel_order = fields.Integer("Time limit to cancel the order", default=12)
    cancellation_reason_for_picking_id = fields.Many2one("order.fill.error.picking",string="Cancellation Reason for Picking")

    def _search_get_details(self, search_type, order, options):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: This method will give products and product types as per brands and as per
            the product type respectively and added to the controller.
        """
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['products_only'] and options.get('stock_type'):
            stock_type = options.get('stock_type')
            domain = []
            if stock_type == 'instock':
                in_stock_prod = request.env['product.product'].sudo().with_context(
                    warehouse_id=self._get_website_location_type()).search([('free_qty', '>', 0)]).mapped(
                    'product_tmpl_id').ids
                domain = [('id', 'in', in_stock_prod)]
            if stock_type == 'presale':
                domain = [('available_for_presale', '=', True),
                          ('product_variant_ids.presale_qty', '>', 0)]
            if stock_type == 'preorder':
                domain = [('available_for_preorder', '=', True),
                          ('product_variant_ids.preorder_qty', '>', 0)]
            if stock_type == 'international':
                domain = [('is_international_pre_order_product', '=', True),
                          ('exclusive_partner_id', 'in', [request.env.user.partner_id.id, False])]
            if stock_type == 'nextshippingday':
                in_stock_prod = request.env['product.product'].sudo().with_context(
                    warehouse_id=self._get_website_location_type()).search([('free_qty', '>', 0)]).mapped(
                    'product_tmpl_id').ids
                domain = [('id', 'in', in_stock_prod),('next_day_shipping', '=', True)]
            result[0]['base_domain'][0].extend(domain)
        return result

    def sale_get_order(self, *args, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: called the sale_get_order to add the location.
        """
        so = super().sale_get_order(*args, **kwargs)
        locations = self._get_website_location_type()
        return so.with_context(locations=locations, warehouse=False)

    def _get_website_location_type(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: return the warehouses as per the filled in the settings(configuration).
        """
        conf_warehouses = []
        self = self.with_user(SUPERUSER_ID)
        if self.stock_pick_type == 'Specific':
            conf_warehouses = (self.warehouse_default_id.ids if self.warehouse_default_id else [])
        elif self.stock_pick_type == 'Several':
            conf_warehouses = (self.warehouse_default_ids.ids if self.warehouse_default_ids else [])
        return conf_warehouses
