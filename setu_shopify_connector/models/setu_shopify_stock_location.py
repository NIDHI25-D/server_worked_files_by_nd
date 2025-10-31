# -*- coding: utf-8 -*-

import time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from .. import shopify
from ..shopify.pyactiveresource.connection import ClientError


class SetuShopifyStockLocation(models.Model):
    _name = 'setu.shopify.stock.location'
    _description = 'Shopify Stock Location'

    is_stock_primary_location = fields.Boolean(string="Stock Location Primary")
    is_fulfillment_stock_legacy_location = fields.Boolean(string='Fulfillment Stock Legacy Location')

    name = fields.Char(string="Stock Location Name", translate=True)
    shopify_location_id = fields.Char(string="Shopify Location")

    active = fields.Boolean(default=True)

    import_stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    odoo_company_id = fields.Many2one('res.company', string='Company', readonly=True)
    order_from_warehouse_id = fields.Many2one('stock.warehouse', string="Order From Warehouse")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)

    export_stock_warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')