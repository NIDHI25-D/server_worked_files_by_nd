from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    associate_pos_ids = fields.One2many('associate.pos.invoice.to.bank.statement', 'invoice_id')
    related_statement_ids = fields.Many2many('account.bank.statement.line', compute='_get_statements')

    def _get_statements(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: This method will give related statements in account.move of POS order as per the invoice mentioned in associate invoices
        """
        for inv in self:
            inv.related_statement_ids = inv.associate_pos_ids.statement_line_id.ids
