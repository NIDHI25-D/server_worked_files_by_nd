from odoo import models, fields, _, api
from odoo.exceptions import UserError, ValidationError

class AssociatePurchaseOrderWithBankStatement(models.Model):
    _name = 'associate.purchase.order.with.bank.statement'

    signed_amount = fields.Float(string="Total Signed")
    statement_line_id = fields.Many2one('account.bank.statement.line')
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Orders")

    @api.onchange('purchase_order_id')
    def calculate_signed_amount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: calculate the signed amount from the  purchase orders in lines.
        """

        for aso in self:
            if len(aso.purchase_order_id.associate_order_ids) == 1 and aso.purchase_order_id.associate_order_ids.id == aso.id:
                continue
            if aso.purchase_order_id.associate_order_ids.filtered(lambda ap: ap.id != aso.id):
                aso.signed_amount = aso.purchase_order_id.amount_total - sum(list((map(abs,
                                                                                       aso.purchase_order_id.associate_order_ids.filtered(
                                                                                           lambda ap: ap.id != aso.id).mapped(
                                                                                           'signed_amount')))))
            else:
                aso.signed_amount = aso.purchase_order_id.amount_total
            if aso.statement_line_id.amount < 0:
                aso.signed_amount = -aso.signed_amount

    @api.onchange('purchase_order_id')
    def onchange_purchase_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: added a domain to see only needed PO in dropdown of the field.
        """

        fully_associated_ids = self.env['purchase.order'].search([]).filtered(
            lambda l: round(sum((map(abs, l.associate_order_ids.mapped('signed_amount')))),
                            2) == l.amount_total and l.amount_total).ids
        return {'domain': {
            'purchase_order_id': [('state', 'not in', ['draft', 'cancel']),
                                  ('id', 'not in', self.statement_line_id.associate_purchase_order_ids.purchase_order_id.ids),
                                  ('id', 'not in', fully_associated_ids)]}}

    @api.constrains('signed_amount')
    def check_signed_amount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: raise validation if condition are not fulfilled.
        """

        for aso in self:
            if sum(list(map(abs, aso.purchase_order_id.associate_order_ids.mapped(
                    'signed_amount')))) > aso.purchase_order_id.amount_total:
                raise ValidationError(
                    _(f"Signed amount of '{aso.purchase_order_id.name}' is more then the total amount of  that Order"
                      f""))
        if aso.statement_line_id.amount > 0 and (aso.statement_line_id.difference_of_purchase_order_with_statement_line < 0):
            raise UserError(
                _("Difference of total of line and total of associated purchase orders is negative please enter valid amount"))
        elif aso.statement_line_id.amount < 0 and (aso.statement_line_id.difference_of_purchase_order_with_statement_line > 0):
            raise UserError(
                _("Difference of total of line and total of associated purchase orders is positive please enter valid amount"))
