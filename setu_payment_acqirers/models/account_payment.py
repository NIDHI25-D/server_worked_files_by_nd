import logging

_logger = logging.getLogger(__name__)
from odoo import models
import stripe

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    def action_post(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 06/12/24
            Task: Migration to v18 from v16
            Purpose: If payment received from the stripe and sale order was confirmed then lock the sale orders.
            2) save latest charge in sale order , received in intent confirmation
        """
        res = super(AccountPayment, self).action_post()
        transaction_id = self.payment_transaction_id
        so = transaction_id.sale_order_ids
        for sale_order in so:
            vals = {}
            if sale_order and sale_order.state == 'sale' and (transaction_id.provider_id.id == self.env.ref(
                    'payment.payment_provider_stripe').id):
                payment_intent = transaction_id.payment_intent
                stripe.api_key = transaction_id.provider_id.stripe_secret_key
                intent = stripe.PaymentIntent.retrieve(payment_intent)
                if intent.get('status') == 'succeeded':
                    if latest_charge := intent.get('latest_charge'):
                        vals.update({'latest_charge_stripe': latest_charge})

                vals.update({'locked': True})
                sale_order.write(vals)
                _logger.info(f" Stripe ({sale_order.name} -Action done")
        return res
