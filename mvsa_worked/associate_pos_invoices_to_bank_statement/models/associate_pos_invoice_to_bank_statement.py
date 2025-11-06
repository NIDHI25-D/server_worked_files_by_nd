from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AssociatePosInvoiceToBankStatement(models.Model):
    _name = 'associate.pos.invoice.to.bank.statement'
    _description = "AssociatePosInvoiceToBankStatement"

    signed_amount = fields.Float(string="Total Signed", compute="calculate_signed_amount", store=True)
    statement_line_id = fields.Many2one('account.bank.statement.line')
    invoice_id = fields.Many2one('account.move', string="Invoices")

    @api.depends('invoice_id')
    def calculate_signed_amount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose:  This method is used to calculate signed amount
        """
        _logger.debug("Compute calculate_signed_amount method start")
        for aso in self:
            if len(aso.invoice_id.associate_pos_ids) == 1 and aso.invoice_id.associate_pos_ids.id == aso.id:
                continue
            if aso.invoice_id.associate_pos_ids.filtered(lambda ap: ap.id != aso.id):
                aso.signed_amount = aso.invoice_id.amount_total - sum(
                    aso.invoice_id.associate_pos_ids.filtered(lambda ap: ap.id != aso.id).mapped('signed_amount'))
            else:
                aso.signed_amount = aso.invoice_id.amount_total
        _logger.debug("Compute calculate_signed_amount method end")

    @api.onchange('invoice_id')
    def onchange_product_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: This method is called while invoices are being changed from Statement line, it will give those
                only invoices which are paid and pos_order_ids not equal to False
        """
        fully_associated_ids = self.env['account.move'].search([('pos_order_ids', '!=', False)]).filtered(
            lambda l: sum(l.associate_pos_ids.mapped('signed_amount')) == l.amount_total).ids
        return {'domain': {
            'invoice_id': [('pos_order_ids', '!=', False),
                           ('id', 'not in', self.statement_line_id.associate_invoice_ids.invoice_id.ids),
                           ('id', 'not in', fully_associated_ids)]}}

    @api.constrains('signed_amount')
    def check_signed_amount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 01/01/25
            Task: Migration to v18 from v16
            Purpose: This Error is raised when signed amount of statement line is increased from total amount
        """
        for aso in self:
            if sum(aso.invoice_id.associate_pos_ids.mapped('signed_amount')) > aso.invoice_id.amount_total:
                raise ValidationError(
                    _(f"Signed amount of '{aso.invoice_id.name}' is more then the total amount of  that invoice"))
