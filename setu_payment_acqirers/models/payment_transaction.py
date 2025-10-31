from odoo import fields, models, api, _
from odoo.http import request
from odoo.exceptions import ValidationError

class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    payment_intent = fields.Char(string="Payment Intent")
    stripe_payment_method= fields.Char(string="Stripe Payment Method")

    def _stripe_prepare_payment_intent_payload(self):
        """
               Authour:sagar.pandya@setconsulting.com
               Date: 11/04/25
               Task: 18 Migration
               Purpose: if payment method is card then , enable installment
               => update payment_method_options in create intent object(payload)
        """
        res =  super()._stripe_prepare_payment_intent_payload()
        if self.provider_id.code == 'stripe' and self.provider_id.enable_monthly_installment:
            if res.get('payment_method_types[]'):
                payment_method_types = res.get('payment_method_types[]')
                if payment_method_types == 'card' and self.stripe_payment_method:
                    res.update({
                        'payment_method':self.stripe_payment_method,
                        'payment_method_options[card][installments][enabled]': True,
                    })
        return res

    def _stripe_prepare_setup_intent_payload(self):
        """
               Authour:sagar.pandya@setconsulting.com
               Date: 11/04/25
               Task: 18 Migration
               Purpose: if payment method is card then , enable installment
               => update payment_method_options in setup intent object(payload)
        """
        res =  super()._stripe_prepare_setup_intent_payload()
        if self.provider_id.code == 'stripe' and self.provider_id.enable_monthly_installment:
            if res.get('payment_method_types[]'):
                payment_method_types = res.get('payment_method_types[]')
                if payment_method_types == 'card'and self.stripe_payment_method:
                    res.update({
                        'payment_method': self.stripe_payment_method,
                        'payment_method_options[card][installments][enabled]': True,
                    })
        return res

    def _stripe_create_intent(self):
        """
         Authour:sagar.pandya@setconsulting.com
               Date: 16/04/25
               Task: 18 Migration
               Purpose: save payment intent id in payment transaction
        """
        res = super()._stripe_create_intent()
        if 'id' in res:
            self.payment_intent = res['id']
        return res
