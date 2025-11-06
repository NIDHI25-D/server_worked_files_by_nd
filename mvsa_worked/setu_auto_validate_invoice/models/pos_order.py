from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _create_invoice(self, move_vals):
        """
            Author: siddharth@setuconsulting.com
            Date: 14/04/25
            Task: The return credit note is automatically signed
            Purpose: When disable_inv_automatic_sign is select then it will create invoice to the draft state.
        """
        res = super()._create_invoice(move_vals)
        for invoice in res:
                disable_inv_sign_check = self.env['ir.config_parameter'].sudo().get_param(
                    'setu_auto_validate_invoice.disable_inv_automatic_sign') or False
                documents = hasattr(invoice.partner_id, 'disable_inv_automatic_sign') and invoice.filtered(
                    lambda doc: not doc.partner_id.disable_inv_automatic_sign) or False
                if (bool(disable_inv_sign_check) or not documents) or invoice.move_type == 'out_refund':
                    return invoice.with_context(is_from_pos_order=True)
        return res

    def _apply_invoice_payments(self, is_reverse=False):
        """
            Author: siddharth@setuconsulting.com
            Date: 14/04/25
            Task: The return credit note is automatically signed
            Purpose: For not apply the invoice payments when disable_inv_sign_check is selected.
        """
        disable_inv_sign_check = self.env['ir.config_parameter'].sudo().get_param(
            'setu_auto_validate_invoice.disable_inv_automatic_sign') or False
        if bool(disable_inv_sign_check) or self.account_move.move_type == 'out_refund':
            return self.env['account.move']
        return super(PosOrder, self)._apply_invoice_payments(is_reverse=is_reverse)
