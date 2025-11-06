from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_move_ids = fields.One2many('account.move', 'related_po', string='Account Move')

    def action_view_invoice(self, invoice=False):
        """
            Author: jay.garach@setuconsulting.com
            Date: 11/03/25
            Task: Migration from V16 to V18 Enhancements Vendor Bill in PO.
            Purpose: To set the current vendor bill in po which is selected in the Related PO field
        """
        rec = super(PurchaseOrder, self).action_view_invoice(invoice)
        invoices = self.account_move_ids
        if invoices:
            if rec['type'] == 'ir.actions.act_window_close':
                rec = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
            rec['domain'] = [('id', 'in', self.invoice_ids.ids + invoices.ids)]
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in rec:
                if len(self.invoice_ids.ids + invoices.ids) > 1:
                    rec['views'] = [(state, view) for state, view in rec['views'] if view != 'form'] + form_view
                else:
                    rec['views'] = form_view
                    rec['res_id'] = invoices.id
        return rec

    @api.depends('invoice_ids', 'account_move_ids')
    def _compute_invoice(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/02/25
            Task: Migration from V16 to V18 (Enhancements Vendor Bill in PO.)
            Purpose: To count the moves.
        """
        super(PurchaseOrder, self)._compute_invoice()
        for order in self:
            order.invoice_count += len(order.account_move_ids)
