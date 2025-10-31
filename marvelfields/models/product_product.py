# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools


class ProductProduct(models.Model):
    _inherit = "product.product"

    length = fields.Float(string="Length")
    whidth = fields.Float(string="Whidth")
    high = fields.Float(string="High")
