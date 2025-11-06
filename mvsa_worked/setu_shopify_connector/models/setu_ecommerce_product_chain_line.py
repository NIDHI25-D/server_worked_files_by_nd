# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import time


class SetuEcommerceProductChainLine(models.Model):
    _inherit = 'setu.ecommerce.product.chain.line'

    import_product_image_status = fields.Selection([('pending', 'Pending'), ('done', 'Done')], default='done',   string="Import Product Image Status")