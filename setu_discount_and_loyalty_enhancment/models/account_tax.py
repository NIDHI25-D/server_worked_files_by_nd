# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    ewallet_invoice_account_id = fields.Many2one(comodel_name='account.account', string='E-wallet Invoice Account')
