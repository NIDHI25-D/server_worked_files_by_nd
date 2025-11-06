# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    shopify_transaction_id = fields.Char(string="Shopify Transaction ID")
    shopify_transaction_type = fields.Selection([('charge', 'Charge'), ('refund', 'Refund'), ('dispute', 'Dispute'),
                                                 ('reserve', 'Reserve'), ('adjustment', 'Adjustment'),
                                                 ('credit', 'Credit'), ('debit', 'Debit'),
                                                 ('payout', 'Payout'), ('payout_failure', 'Payout Failure'),
                                                 ('payout_cancellation', 'Payout Cancellation'), ('fees', 'Fees'),
                                                 ('payment_refund', 'Payment Refund')],
                                                string="Shopify Transaction Type")
