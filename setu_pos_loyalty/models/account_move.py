from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    loyalty_points_earned = fields.Float(string="Earned Points", default=0,
                                         help='The number of Loyalty Points that the customer has earned from this '
                                              'order.',
                                         copy=False)
    is_pos_invoice = fields.Boolean(string="POS Invoice?", compute="is_pos_invoices")

    def is_pos_invoices(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 13/05/2025
            Task: Migration from V16 to V18
            Purpose: It will set fields is_pos_invoice = True if invoice is generated from the pos orders else set values False.
        """
        for record in self:
            pos_invoice = self.env['pos.order'].search([('account_move', '=', record.id)])
            if pos_invoice:
                record.is_pos_invoice = True
            else:
                record.is_pos_invoice = False
