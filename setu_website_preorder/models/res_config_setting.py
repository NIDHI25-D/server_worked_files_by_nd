from odoo import fields, models, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_pre_order = fields.Boolean(string='Enable PreOrder', readonly=False,
                                      related="website_id.enable_pre_order")
    enable_pre_sale = fields.Boolean(string='Enable PreSale', readonly=False,
                                     related="website_id.enable_pre_sale")

    stock_pick_type = fields.Selection(related="website_id.stock_pick_type", readonly=False,
                                       string="Default Stock Location")
    stock_location = fields.Many2one("stock.location", readonly=False,
                                     related="website_id.default_stock_location",
                                     string="Stock Location",
                                     domain="[('usage', '=', 'internal')]")
    stock_location_ids = fields.Many2many("stock.location", readonly=False,
                                          related="website_id.default_stock_location_ids",
                                          string="Stock Locations",
                                          domain="[('usage', '=', 'internal')]")
    quantity_type = fields.Selection(related="website_id.quantity_type", readonly=False,
                                     string="Stock Out Type")
    display_quantity = fields.Boolean(string="Display Product Quantity On Website",
                                      related="website_id.display_quantity")
    warehouse_id = fields.Many2one("stock.warehouse", readonly=False,
                                   related="website_id.warehouse_id", string="Stock Warehouse")
    warehouse_default_id = fields.Many2one("stock.warehouse", readonly=False,
                                        related="website_id.warehouse_default_id", string="Default Warehouse")
    warehouse_default_ids = fields.Many2many("stock.warehouse", readonly=False,
                                             related="website_id.warehouse_default_ids", string="Default Warehouses")
    presale_exchange_rate = fields.Float(related="website_id.presale_exchange_rate", readonly=False)
    presale_pricelist = fields.Many2one(related="website_id.presale_pricelist", string="Presale Pricelist",readonly=False)
    excluded_pricelist_id = fields.Many2one(related="website_id.excluded_pricelist_id", string="Excluded Pricelist",readonly=False)
    cash_payment = fields.Float(related="website_id.cash_payment", string="Cash Payment", readonly=False)
    available_qty_multiplier = fields.Integer(related="website_id.available_qty_multiplier", string="Available Quantity Multiplier", readonly=False)
    minimum_amt_qty = fields.Integer(related="website_id.minimum_amt_qty", string="Minimum Amount Quantity", readonly=False)
    days_for_calculation = fields.Integer(related="website_id.days_for_calculation", string="Configure Days for Website Available Quantity", readonly=False)
    international_preorder_msg = fields.Html(related="website_id.international_preorder_msg",string="International Preorder Message", readonly=False)
    intl_preorder_pricelist_id = fields.Many2one(related="website_id.intl_preorder_pricelist_id", string="International Preorder Pricelist",
                                        readonly=False)
    cash_next_day_pricelist_id = fields.Many2one(related="website_id.cash_next_day_pricelist_id",
                                                 string="Cash Next Day Specific Pricelist",
                                                 readonly=False)
    credit_next_day_pricelist_id = fields.Many2one(related="website_id.credit_next_day_pricelist_id",
                                                 string="Credit Next Day Specific Pricelist",
                                                 readonly=False)
    presale_msg = fields.Html(related="website_id.presale_msg",string="Presale Message", readonly=False)
    activity_owner_ids = fields.Many2many('res.users', related="website_id.activity_owner_ids", string="Activity User", readonly=False)
    config_quantity = fields.Float(related="website_id.config_quantity", string="Config Quantity", readonly=False)
    enable_cancellation_sale_order = fields.Boolean(string="Enable Website sale orders cancellation",readonly=False,
                                      related="website_id.enable_cancellation_sale_order")
    time_limit_to_cancel_order = fields.Integer("Time limit to cancel the order",readonly=False,related="website_id.time_limit_to_cancel_order")
    cancellation_reason_for_picking_id = fields.Many2one(related="website_id.cancellation_reason_for_picking_id",
                                                     string="Cancellation Reason for Picking",
                                                 readonly=False)
