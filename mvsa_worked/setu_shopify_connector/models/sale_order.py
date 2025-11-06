# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime
import requests

import pytz
from odoo import models, fields, api, _

utc = pytz.utc

from .. import shopify
from ..shopify.pyactiveresource.connection import ClientError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_shopify_order_status(self):
        for order_id in self:
            if order_id.multi_ecommerce_connector_id:
                pickings = order_id.picking_ids.filtered(lambda x: x.state != "cancel")
                if pickings:
                    outgoing_picking = pickings.filtered(lambda x: x.location_dest_id.usage == "customer")
                    if all(outgoing_picking.mapped("is_updated_shopify_delivery")):
                        order_id.is_shopify_order_updated = True
                        continue
                if order_id.state != 'draft':
                    move_ids = self.env["stock.move"].search(
                        [("picking_id", "=", False), ("sale_line_id", "in", order_id.order_line.ids)])
                    state = set(move_ids.mapped('state'))
                    if len(set(state)) == 1 and 'done' in set(state):
                        order_id.is_shopify_order_updated = True
                        continue
                order_id.is_shopify_order_updated = False
                continue
            order_id.is_shopify_order_updated = False

    is_shopify_risk_order = fields.Boolean(string="Risk Order", default=False, copy=False)
    is_shopify_order_updated = fields.Boolean(string="Order Updated On Shopify", compute=_get_shopify_order_status,
                                              search='_search_shopify_order_ids')

    is_shopify_pos_order = fields.Boolean(string="Shopify Pos Order", copy=False)
    is_shopify_cancelled_order = fields.Boolean(string="Order Cancelled In Shopify", default=False, copy=False)
    is_shopify_service_tracking_update = fields.Boolean(string="Order Tracking Updated", default=False, copy=False)

    shopify_order_id = fields.Char(string="Shopify Order ID", copy=False)
    shopify_order_number = fields.Char(string="Shopify Order Number", copy=False)
    shopify_order_status = fields.Char(string="Shopify Order Status", copy=False)

    order_close_date = fields.Datetime(string="Order Close", copy=False)

    setu_shopify_payment_gateway_id = fields.Many2one('setu.shopify.payment.gateway', string="Shopify Payment Gateway",
                                                      copy=False)
    setu_shopify_location_id = fields.Many2one("setu.shopify.stock.location", "Shopify Location", copy=False)

    setu_shopify_risky_order_ids = fields.One2many('setu.shopify.risky.order', 'sale_order_id', string="Risks",
                                                   copy=False)
    setu_shopify_transaction_order_ids = fields.One2many('setu.shopify.transaction.order', 'sale_order_id',
                                                         string="Transaction")
