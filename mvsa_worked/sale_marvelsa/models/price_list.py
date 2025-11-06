# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PriceList(models.Model):
    _inherit = 'product.pricelist'

    is_credit = fields.Boolean(string="Is Credit ?")
    payment_term_for_priceslist_id = fields.Many2one('account.payment.term', string="Payment term")
