# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger("picking_isuues")
from odoo import fields, models,api,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_from_website = fields.Boolean('Is from Website', default=False,copy=False)
    is_amazon_order_manually = fields.Boolean("Is Amazon order manually created?", default=False, copy=False)

