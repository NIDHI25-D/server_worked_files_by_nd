# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemporary(models.Model):
    _name = 'product.temporary'
    _description = "Product Temporary"

    name = fields.Char(string="Name")
