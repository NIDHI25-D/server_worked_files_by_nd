
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentPortal
import logging
from werkzeug.exceptions import Forbidden
import hmac
from hashlib import sha256
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing



_logger = logging.getLogger(__name__)



class BbvaController(http.Controller):
    _success_url = '/payment/bbva/success'
    _cancel_url = '/payment/bbva/cancel'

    @http.route(
        ['/payment/bbva/success', '/payment/bbva/cancel'], type='http', auth='public', methods=['GET','POST'], csrf=False)
    def bbva_return_from_checkout(self, **data):
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('bbva', data)
        self._verify_notification_signature(data, tx_sudo)
        tx_sudo._handle_notification_data('bbva', data)
        return request.redirect('/payment/status')


    @staticmethod
    def _verify_notification_signature(notification_data, tx_sudo):
        # Retrieve the received signature from the data
        received_signature = notification_data.get('mp_signature')
        if not received_signature:
            _logger.warning("received notification with missing signature")
            raise Forbidden()

        # Compare the received signature with the expected signature computed from the data
        received_order = notification_data.get('mp_order')
        received_reference = notification_data.get('mp_reference')
        received_amount = notification_data.get('mp_amount')
        received_authorization = notification_data.get('mp_authorization')
        secret_key =  tx_sudo.provider_id.secret_key
        concate_key = f"""{received_order}{received_reference}{received_amount}{received_authorization}"""
        hash_string = hmac.new(secret_key.encode(), concate_key.encode(), sha256).hexdigest()
        if not hmac.compare_digest(received_signature, hash_string):
            _logger.warning("received notification with invalid signature")
            raise Forbidden()

class BbvaPaymentPortal(PaymentPortal):

    def _create_transaction(self,payment_option_id,custom_create_values,*args, provider_reference=None, **kwargs):
        provider_id = request.env['payment.provider'].sudo().browse(payment_option_id)
        if provider_id and provider_id.code == 'bbva':
            payment_transaction_id = request.env['payment.transaction'].sudo().search([('sale_order_ids','in',custom_create_values.get('sale_order_ids')[0][2]),('state','=','draft')], order='id desc',limit=1)
            if payment_transaction_id:
                payment_transaction_id._log_sent_message()
                PaymentPostProcessing.monitor_transactions(payment_transaction_id)
                return payment_transaction_id
        return super()._create_transaction(*args,payment_option_id=payment_option_id,custom_create_values=custom_create_values, provider_reference=provider_reference, **kwargs)
