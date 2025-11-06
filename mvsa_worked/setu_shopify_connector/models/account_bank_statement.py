# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    shopify_payment_ref = fields.Char(string='Shopify Payment Reference')
