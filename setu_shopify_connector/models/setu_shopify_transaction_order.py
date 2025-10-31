# -*- coding: utf-8 -*-

from odoo import models, fields


class SetuShopifyTransactionOrder(models.Model):
    _name = "setu.shopify.transaction.order"
    _description = 'Shopify Transaction Order'

    original_shopify_order_id = fields.Char(string="Original Shopify Order")
    authorization = fields.Char(string="Authorization")
    transaction_id = fields.Char(string="Transaction Order ID")
    kind = fields.Char(string="Kind")
    source_name = fields.Char(string="Source", translate=True)
    status = fields.Char(string="Status")

    message = fields.Text(string="Order Message", translate=True)

    sale_order_id = fields.Many2one("sale.order", string="Order")