# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SetuShopifyOrderStatus(models.Model):
    _name = "setu.shopify.order.status"
    _description = 'Shopify Order Status'

    name = fields.Char(string="Name", translate=True)
    status = fields.Char(string="Order Status")
