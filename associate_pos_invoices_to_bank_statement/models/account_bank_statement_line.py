from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    difference_of_invoices_with_statement_line = fields.Float(compute="calculate_difference", store=True)
    invoice_ids = fields.Many2many('account.move', 'statement_line_move_rel', 'statement_id', 'invoice_id')
    associate_invoice_ids = fields.One2many('associate.pos.invoice.to.bank.statement', 'statement_line_id')
    total_signed = fields.Float(compute="calculate_total_signed")

    def open_wizard_to_associate_invoices(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to open a wizard for Associate Invoices.
            Procedure : Accounting(dashboard) with reconcile items(Bank Reconciliation)-> List view -> in lines associate button
        """
        view = self.env.ref('associate_pos_invoices_to_bank_statement.bank_statement_line_form_view')
        return {
            'name': _('Statement Line'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.id,
            'target': 'new',
            'context': {'line_id': self.id}
        }

    @api.depends('associate_invoice_ids')
    def calculate_difference(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to
                calculate the difference_of_invoices_with_statement_line and mention in list and wizard
        """
        _logger.debug("Compute calculate_difference method start")
        for rec in self:
            total = sum(rec.associate_invoice_ids.filtered(
                lambda line: line.invoice_id).mapped('signed_amount'))
            rec.difference_of_invoices_with_statement_line = rec.amount_total - total
        _logger.debug("Compute calculate_difference method end")

    def calculate_total_signed(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: this method will assign total_signed of invoices per line
        """
        _logger.debug("Compute calculate_total_signed method start")
        active_invoice = self.env['account.move'].browse(self._context.get('invoice'))
        for line in self:
            line.total_signed = sum(
                line.associate_invoice_ids.filtered(
                    lambda i: i.invoice_id.id == active_invoice.id).mapped('signed_amount'))
        _logger.debug("Compute calculate_total_signed method end")
