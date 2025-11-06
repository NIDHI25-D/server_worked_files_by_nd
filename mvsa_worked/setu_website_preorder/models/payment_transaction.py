from odoo import models, fields, _
from odoo.http import request


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _check_amount_and_confirm_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/04/25
            Task: Migration to v18 from v16
            Purpose: if the order are preorder or presale so attach the transaction with sale order and post the message.
        """
        presale_preorder_orders = self.sale_order_ids.filtered(
            lambda so: so.state in ('draft', 'sent') and (so.is_preorder or so.is_presale))
        res = super(PaymentTransaction, self - presale_preorder_orders.transaction_ids)._check_amount_and_confirm_order()
        for order in presale_preorder_orders:
            if order.state in ('draft', 'sent') and (order.is_preorder or order.is_presale):
                order.message_post(
                    body=_(
                        "The order was not confirmed as %s type of order") % (
                             'Pre Sale' if order.is_presale else 'Pre Order'
                         )
                )
                self.write({'is_post_processed': True})
                res |= order
        return res
