# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = "product.product"

    journal_id = fields.Many2one('account.journal', string='Journal')
