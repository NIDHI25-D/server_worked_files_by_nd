# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .. import shopify


class SetuShopifyWebhook(models.Model):
    _name = "setu.shopify.webhook"
    _description = 'Shopify Webhook'

    name = fields.Char(string='Name', translate=True)
    webhook_id = fields.Char(string='Webhook ID')
    base_url = fields.Char(string="Base URL")

    state = fields.Selection([('active', 'Active'), ('disabled', 'Disabled'), ('paused', 'Paused')], default='disabled',
                             string="Hook State")

    operations = fields.Selection([('orders/create', 'Order Create'),
                                   ('customers/create', 'Customer Create'),
                                   ('customers/update', 'Customer Update'),
                                   ('products/update', 'Product Update'),
                                   ('products/delete', 'Product Delete')], default='orders/create', string="Operations")

    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', ondelete="cascade")