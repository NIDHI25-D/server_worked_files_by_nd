# -*- coding: utf-'8' "-*-"

try:
    import simplejson as json
except ImportError:
    import json
import logging
import pprint

from odoo import osv, fields, models, api, _

import mercadopago
from odoo.addons.payment_mercado_pago.controllers.main import MercadoPagoController
from odoo.exceptions import UserError, ValidationError
from werkzeug import urls
_logger = logging.getLogger(__name__)


class TxMercadoPago(models.Model):
    _inherit = 'payment.transaction'



    def _get_provider(self):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/23
            Task: 18 Migration
            Purpose: It will set the payment provider's code during the open of payment transactions.
            note : to use in invisible condition of transaction view
        """
        for tx in self:
            tx.mercadopago_txn_provider = tx.provider_id.code


    mercadopago_payment_id = fields.Char('Payment ID', index=True)
    mercadopago_txn_type = fields.Char('Transaction type', index=True)
    mercadopago_txn_provider = fields.Char(string="Transaction Provider", compute=_get_provider)
    date = fields.Datetime(string="Transaction Date and Time")
    fees = fields.Monetary(
        string="Fees", currency_field='currency_id',
        help="The fees amount; set by the system as it depends on the provider", readonly=True)

    # def _send_payment_request(self):
    #     """ Override of payment to send a payment request to Stripe with a confirmed PaymentIntent.


    def _mercadopago_create_payment_intent(self, acquirer_ref=None, email=None,data=None):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/23
            Task: 18 Migration
            Purpose:
                     1) it will update installments months as installment id in odoo
                     2) prepare payment request data, It will create Payment into the Mercado pago's Platform
        """
        sdk = mercadopago.SDK(self.provider_id.mercado_pago_access_token)
        installments_months = 0
        if self.env['ir.module.module'].search([('name', '=', 'setu_payment_acqirers'), (
                'state', '=', 'installed')]) and (self.token_id.applied_installment_id or data.get('applied_installment_id')):
            mercadopago_installments_obj = self.env['monthly.installment'].sudo().browse(
                self.token_id.applied_installment_id or data.get('applied_installment_id'))
            installments_months = mercadopago_installments_obj.months
        # customer_name = self.payment_token_id.name.split('-')
        # if len(customer_name) == 3:
        #     customer_name = customer_name[-1].strip()
        # else:
        payment_transaction = data.get('mp_payment_transaction')
        customer_name = self.sale_order_ids.partner_id.name if not payment_transaction.invoice_ids else payment_transaction.invoice_ids.partner_id.name
        payment_data = {
            "transaction_amount": round(self.amount, 2),
            "token": self.token_id.mercadopago_cards_token or data.get('mercadopago_cards_token'),
            "description": "Payment for " + self.sale_order_ids.display_name if not payment_transaction.invoice_ids else payment_transaction.invoice_ids.name,
            "installments": installments_months or 1,
            "payment_method_id": self.token_id.mercadopago_payment_method or data.get('mercadopago_payment_method'),
            "payer": {
                "email":  'test_payer_11445@testuser.com' if self.provider_id.state == 'test' else self.sale_order_ids.partner_id.email if not payment_transaction.invoice_ids else payment_transaction.invoice_ids.partner_id.email ,
                "first_name": customer_name,
            },
            "capture": True
        }
        if (self.token_id.mercadopago_card_issuer_name or data.get('mercadopago_card_issuer_name')) == 'American Express':
            payment_data.update({'capture': False})
        _logger.info('MercadoPago(%s) _mercadopago_create_payment_intent : Sending values to Mercado Pago, values:\n%s',
                     self.sale_order_ids[0].name  if not payment_transaction.invoice_ids else  payment_transaction.invoice_ids.name, pprint.pformat(payment_data))
        payment_response = sdk.payment().create(payment_data)
        _logger.info('MercadoPago(%s) _mercadopago_create_payment_intent : Values received:\n%s',
                     self.sale_order_ids[0].name  if not payment_transaction.invoice_ids else  payment_transaction.invoice_ids.name, pprint.pformat(payment_response))
        if payment_response['status'] == 201:
            if (self.token_id.mercadopago_card_issuer_name or data.get('mercadopago_card_issuer_name'))== 'American Express':
                payment_data = {"capture": True}
                payment_id = payment_response['response'].get('id')
                payment_response = sdk.payment().update(payment_id, payment_data)
                _logger.info(
                    f"MercadoPago({self.sale_order_ids[0].name  if not payment_transaction.invoice_ids else  payment_transaction.invoice_ids.name}) - American express Payments Updates response :- {payment_response}")


            if payment_response.get('response') and payment_response.get('response').get('fee_details'):
                for fee in payment_response.get('response').get('fee_details'):
                    if fee.get('fee_payer') == 'collector':
                        self.fees = fee.get('amount')



            # if payment_response.get('response').get('status') == :
            # payment = payment_response["response"]
        else:
            return payment_response
        return payment_response

    def _mercadopago_s2s_validate_tree(self, tree):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/23
            Task: 18 Migration
            Purpose: It will Validate the response which ias received while register payment into the Mercado pago's platform.
        """
        self.ensure_one()
        _logger.info(f"MercadoPago({self.sale_order_ids[0].name  if not self.invoice_ids else  self.invoice_ids.name}) -Start validation of payment response tree :- {tree}")
        if self.state not in ("draft", "pending"):
            _logger.info('MercadoPago(%s): trying to validate an already validated tx (ref %s)',
                         self.sale_order_ids[0].name  if not self.invoice_ids else  self.invoice_ids.name, self.reference)
            return True
        status = tree.get('status')
        tx_id = tree.get('id')
        vals = {
            "date": fields.datetime.now(),
            "mercadopago_payment_id": tx_id,
        }
        if status == 'approved':
            self.write(vals)
            self._set_done()
            # self._execute_callback()
            # TODO : needs toes does saves cards details
            # if self.type == 'form_save':
            #     s2s_data = {
            #         'customer': tree.get('customer'),
            #         'payment_method': tree.get('payment_method'),
            #         'card': tree.get('payment_method_details').get('card'),
            #         'acquirer_id': self.acquirer_id.id,
            #         'partner_id': self.partner_id.id
            #     }
            # token = self.acquirer_id.stripe_s2s_form_process(s2s_data)
            # self.token_id = token.id
            # if self.token_id:
            #     self.token_id.verified = True
            # return True
        if status in ('pending', 'in_process'):
            self.write(vals)
            self._set_pending()
            return True
        if status in ('rejected', 'cancelled'):
            self._set_canceled()
            # Needs toes cancels the payments usoins api ins mercadopagoes servers websites
            # self.acquirer_id._stripe_request('payment_intents/%s/cancel' % self.stripe_payment_intent)
            return False
        else:
            error = tree.get("message")
            self._set_error(error)
            return False

    def mercadopago_s2s_do_transaction(self,data):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/23
            Task: 18 Migration
            Purpose: It will register the payment with validate it. and change the payment transactions state accordings it.
        """
        self.ensure_one()
        # Creates payments
        result = self._mercadopago_create_payment_intent(acquirer_ref=self.token_id.provider_ref,
                                                         email=self.partner_email,data=data)
        _logger.info(f"MercadoPago({self.sale_order_ids[0].name  if not self.invoice_ids else  self.invoice_ids.name}) - Create payment intent methods response :- {result}")
        # Validates payments responses
        return self._mercadopago_s2s_validate_tree(result.get('response'))

    def mercadopago_auto_payment_transaction_status_check_and_update(self):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/23
            Task: 18 Migration
            Purpose: It will done payment  which payment are pending in the previously.
        """
        # mp_pending_payments_transaction_ids = self.env['payment.transaction'].search(
        #     [('state', '=', 'pending'), ('provider_id', '=', self.env.ref(
        #         'setu_payment_mercadopago.payment_acquirer_mercadopago').id)])
        sdk = False
        mp_pending_payments_transaction_ids = self.env['payment.transaction'].search(
            [('state', '=', 'pending'), ('provider_id', '=', self.env.ref(
                'payment.payment_provider_mercado_pago').id)])
        if mp_pending_payments_transaction_ids:
            if mp_pending_payments_transaction_ids[0].provider_id.mercado_pago_access_token:
                # sdk = mercadopago.SDK(mp_pending_payments_transaction_ids[0].provider_id.mercadopago_access_token)
                sdk = mercadopago.SDK(mp_pending_payments_transaction_ids[0].provider_id.mercado_pago_access_token)
        if sdk:
            for pt in mp_pending_payments_transaction_ids:
                payment_id = pt.mercadopago_payment_id
                if payment_id:
                    payment = sdk.payment().get(payment_id)
                    _logger.info(
                        f"mercadopago_auto_payment_transaction_status_check_and_update ==> get payment{pprint.pprint(payment)}")
                    if payment and payment.get('response').get('status') == 'authorized' and payment.get('response').get(
                            'status_detail') == 'pending_capture':
                        payment_data = {"capture": True}
                        res = sdk.payment().update(payment_id, payment_data)
                        _logger.info(
                            f"mercadopago_auto_payment_transaction_status_check_and_update ==> After updating payment{pprint.pprint(res)}")
                        if res and res.get('response').get('status') == 'approved' and res.get('response').get(
                                'status_detail') == 'accredited':
                            pt._set_done()
                            # pt._finalize_post_processing_finalize_post_processing()
                            pt._post_process()


class PaymentTokenMercadoPago(models.Model):
    _inherit = 'payment.token'

    mercadopago_payment_method = fields.Char('Payment Method ID', help="visa,maestro,master card,etc...")
    mercadopago_cards_token = fields.Char('Mercado pago Cards token')
    mercadopago_card_issuer_name = fields.Char('Mercado pago Cards issuer name')
    mercadopago_card_issuer_id = fields.Integer('Mercado pago Cards issuer id')
    mercadopago_payment_type_name = fields.Char('Mercado pago Payment Type name',
                                                help="credit card, debit card, online,etc")

    applied_installment_id = fields.Integer('Customers appyied installments Months')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 04/04/25
            Task: 18 Migration
            Purpose: it will lock sale order if payment successful in Mercado Pago
        """
        res = super(AccountPayment, self).action_post()
        so = self.payment_transaction_id.sale_order_ids
        for sale_order in so:
            if sale_order and sale_order.state == 'sale' and (self.payment_transaction_id.provider_id.id == self.env.ref(
                    'payment.payment_provider_mercado_pago').id):
                # sale_order.action_done()
                sale_order.write({'locked': True})
                _logger.info(f"MercadoPago({sale_order.name} -Action done")
        return res
