# -*- coding: utf-8 -*-

import json
import time
from datetime import datetime, timedelta

from odoo import models, fields, _
from odoo.exceptions import ValidationError

from .. import shopify
from ..shopify.pyactiveresource.connection import ClientError


class SetuShopifyPaymentGateway(models.Model):
    _name = "setu.shopify.payment.gateway"
    _description = "Shopify Payment Gateway"

    active = fields.Boolean(string="Active GateWay", default=True)

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string="Code", required=True)

    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False, required=True)