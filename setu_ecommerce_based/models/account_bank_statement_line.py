from odoo import models, fields


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    reversal_invoice_id = fields.Many2one(comodel_name="account.move", string="Refund Invoice")
