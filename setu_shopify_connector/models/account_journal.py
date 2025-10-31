# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_shopify_payout_journal = fields.Boolean(string="Shopify Payment Journal")
