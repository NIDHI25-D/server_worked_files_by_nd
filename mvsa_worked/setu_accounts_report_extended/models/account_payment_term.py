from odoo import models, fields, api


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    send_debit_balance_report = fields.Boolean(string="Send debit balance report", default=False)