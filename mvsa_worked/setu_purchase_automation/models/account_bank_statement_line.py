from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    difference_of_purchase_order_with_statement_line = fields.Float(compute="calculate_purchase_difference", store=True,
                                                                    string="Difference Of Po With Statement")
    associate_purchase_order_ids = fields.One2many('associate.purchase.order.with.bank.statement', 'statement_line_id')
    po_total_signed = fields.Float(compute="calculate_po_total_signed")

    def open_wizard_to_associate_purchase_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: open wizard from button Associate Purchase Order.
        """
        view = self.env.ref('setu_purchase_automation.bank_statement_line_form_view_for_purchase_order')
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

    @api.depends('associate_purchase_order_ids')
    def calculate_purchase_difference(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: calculate the field Difference Of Po With Statement.
        """
        li_total = sum(self.associate_purchase_order_ids.filtered(lambda ap: ap.purchase_order_id).mapped('signed_amount'))
        self.difference_of_purchase_order_with_statement_line = round(self.amount - li_total, 2) if li_total else 0

    def calculate_po_total_signed(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: compute the total signed of the po which are saved in the current record.
        """
        _logger.debug("Compute calculate_po_total_signed method start")
        active_order = self.env['purchase.order'].browse(self._context.get('order'))
        for line in self:
            line.po_total_signed = sum(
                line.associate_purchase_order_ids.filtered(lambda i: i.purchase_order_id.id == active_order.id).mapped(
                    'signed_amount'))
        _logger.debug("Compute calculate_po_total_signed method end")
