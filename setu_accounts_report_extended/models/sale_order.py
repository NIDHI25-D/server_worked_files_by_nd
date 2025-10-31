# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_move_ids = fields.One2many('account.move', 'related_so_id', string='Account Move')

    def action_view_invoice(self, invoices=False):
        """
            Author: jay.garach@setuconsulting.com
            Date: 11/03/25
            Task: Migration from V16 to V18.
            Purpose: To set the current Sale Order in po which is selected in the Related PO field
        """
        rec = super(SaleOrder, self).action_view_invoice(invoices)
        credit_notes = self.account_move_ids
        if credit_notes:
            if rec['type'] == 'ir.actions.act_window_close':
                rec = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
            rec['domain'] = [('id', 'in', self.invoice_ids.ids + credit_notes.ids)]
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in rec:
                if len(self.invoice_ids.ids + credit_notes.ids) > 1:
                    rec['views'] = [(state, view) for state, view in rec['views'] if view != 'form'] + form_view
                else:
                    rec['views'] = form_view
                    rec['res_id'] = credit_notes.id
        return rec

    @api.depends('order_line.invoice_lines', 'invoice_ids', 'account_move_ids')
    def _get_invoiced(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/02/25
            Task: Migration from V16 to V18
            Purpose: To count the moves.
        """
        super(SaleOrder, self)._get_invoiced()
        for order in self:
            order.invoice_count += len(order.account_move_ids)
