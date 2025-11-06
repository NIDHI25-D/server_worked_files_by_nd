# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_updated_shopify_delivery = fields.Boolean(string="Updated Delivery In Shopify", default=False)
    is_shopify_delivery_order = fields.Boolean(string="Shopify Delivery Order", default=False)
    is_cancelled_in_shopify = fields.Boolean(string="Cancelled In Shopify ?", default=False, copy=False)
    is_manually_action_shopify_fulfillment = fields.Boolean(string="Manually Action Required ?", default=False, copy=False)

    shopify_fulfillment_id = fields.Char(string='Shopify Fulfillment ID')

