# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route
from odoo.addons.payment.controllers import portal as payment_portal


class PaymentPortal(payment_portal.PaymentPortal):

    @route('/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True)
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """
              Author: jay.garach@setuconsulting.com
              Date: 26/12/24
              Task: Migration from V16 to V18
              Purpose: is the general billing True then order invoice address will set as per partner
              general billing address.
        """
        is_billing_general = kwargs.get('is_billing_general', False)
        kwargs.pop('is_billing_general', None)
        res = super().shop_payment_transaction(order_id, access_token, **kwargs)
        order = request.env['sale.order'].sudo().browse(order_id)
        if order and order.partner_id.billing_general_public_id and is_billing_general:
            order.partner_invoice_id = order.partner_id.billing_general_public_id
        return res
