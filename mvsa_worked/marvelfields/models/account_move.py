# -*- coding: utf-8 -*-

from odoo import models, fields, api
import traceback
import logging

_logger = logging.getLogger('invoice_date_due')

class AccountMove(models.Model):
    _inherit = 'account.move'

    dfactura_invoice = fields.Boolean(string='Detener Factura')
    mostrador = fields.Boolean(string='Cliente Mostrador')

    def action_post(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18 (https://app.clickup.com/t/865cgaht4)
            Purpose: this is only for a vendor bill and set the reference if the biil has no payment reference
        """
        res = super(AccountMove, self).action_post()
        for move in self:
            if move.move_type == 'in_invoice' and not move.payment_reference:
                move.line_ids.filtered(lambda x: x.display_type == 'payment_term').name = move.name
        return res

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86dveyewu)
            Purpose: to trace the due date if it is changed by the odoobot.
        """
        if 'invoice_date_due' in vals and self.env.user.id == self.env.ref('base.partner_root').id:
            user = self.env.user
            _logger.info(
                f"{traceback.print_stack()}------tracing_due_date_change: User {user.name} changed the Due Date")
        return super(AccountMove, self).write(vals)

