from odoo import api, fields, models, _
from werkzeug import urls
from hashlib import sha1, sha256
import hmac
from odoo.addons.setu_payment_bbva.controllers.main import BbvaController
import logging
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)


class PaymentAcquirerBbva(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[
        ('bbva', 'Bbva')
    ], ondelete={'bbva': 'set default'})
    secret_key = fields.Char('Secret Key')
    payment_promotion_ids = fields.Many2many('payment.promotion', 'acquirer_promotion_rel', 'acquirer_id',
                                             'promotion_id', string="Payment Promotion")
    customer_id = fields.Char('Customer Id', help='Unique customer identifier')

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist PayUmoney providers when the currency is not INR. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        for i in providers:
            # if self.env.ref('setu_payment_bbva.payment_provider_bbva').id == i.id:
            i = i.with_user(SUPERUSER_ID)
            monthly_installment_ids = i.monthly_installment_ids
            if i.enable_monthly_installment and i.monthly_installment_ids:
                sale_order_id = kwargs.get('sale_order_id', False)
                sale_order = False
                if sale_order_id:
                    sale_order = self.env['sale.order'].browse(sale_order_id)
                    pricelist_id = sale_order.pricelist_id
                    prlist_avil_in_installments = i.monthly_installment_ids.filtered(
                        lambda month_inst: month_inst.pricelist_id.id == pricelist_id.id)
                    if prlist_avil_in_installments:
                        continue
                    else:
                        providers -= i

        return providers

    def get_installment(self, pricelist_id, sale_order, monthly_installment_ids):
        sale_order_amount = sale_order.amount_total
        filtered_pricelist_records = monthly_installment_ids.filtered(
            lambda list_id: list_id.pricelist_id == pricelist_id)
        if filtered_pricelist_records:
            filtered_pricelist_with_amount_records = filtered_pricelist_records.filtered(
                lambda list_id: list_id.minimum_amount <= sale_order_amount)
            if filtered_pricelist_with_amount_records:
                month_list = filtered_pricelist_with_amount_records.mapped('months')
                promotion_list = filtered_pricelist_with_amount_records.mapped('payment_promotion_id.code')
                payment_options_list = filtered_pricelist_with_amount_records.mapped('payment_options_ids.code')
                final_promotion_list = '|'.join(str(m) for m in promotion_list)
                final_month_list = '|'.join(str(m) for m in month_list)
                final_payment_options_list = '|'.join(str(m) for m in payment_options_list)
                return final_month_list, final_promotion_list, final_payment_options_list
        return '', '', ''

    def bbva_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_bbva_urls(environment)['bbva_form_url']


class PaymentTransactionBbva(models.Model):
    _inherit = 'payment.transaction'

    hmac_key = fields.Char("Hmac key")

    def _get_specific_rendering_values(self, processing_values):
        self.ensure_one()
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bbva':
            return res

        bbva_tx_values = dict(processing_values)

        base_url = self.get_base_url()
        order_ref = processing_values.get('reference', '')
        split_order_reference = order_ref.split('-')[0]
        sale_order = self.env['sale.order'].search([('name', '=', split_order_reference)])
        pricelist_id = sale_order.pricelist_id
        payment_transaction = self.env['payment.transaction'].search([('reference', '=', order_ref)])
        payment_refrence = order_ref
        amount = round(processing_values.get('amount'), 2)
        secret_key = self.provider_id.secret_key
        concate_key = f"""{sale_order.id}{payment_refrence}{amount}"""
        hash_string = hmac.new(secret_key.encode(), concate_key.encode(), sha256).hexdigest()
        mail = processing_values.get('billing_partner_email')
        phone = processing_values.get('partner_phone')
        monthly_installment_ids = self.provider_id.monthly_installment_ids
        installment_data = ''
        promotion_data = ''
        final_payment_options_list = ''
        api_url = 'https://%s/clb/endpoint/comercializadoraMarvel' % (
            'prepro.adquiracloud.mx' if self.provider_id.state == 'test' else 'www.adquiramexico.com.mx')
        if self.provider_id.enable_monthly_installment and monthly_installment_ids:
            installment_data, promotion_data, final_payment_options_list = self.provider_id.get_installment(
                pricelist_id, sale_order, monthly_installment_ids)
        bbva_tx_values.update({
            'mp_account': 12686,
            'mp_order': sale_order.id,
            'mp_reference': payment_refrence,
            'mp_product': 1,
            'mp_node': '0',
            'mp_concept': '1',
            'mp_amount': amount,
            'mp_currency': 1 if pricelist_id.currency_id.name == 'MXN' else 2,
            'mp_email': mail,
            'mp_phone': phone,
            "mp_urlsuccess": urls.url_join(base_url, BbvaController._success_url),
            "mp_urlfailure": urls.url_join(base_url, BbvaController._cancel_url),
            "mp_signature": hash_string,
            "mp_promo": promotion_data,
            "mp_promo_msi": installment_data,
            "mp_paymentmethod": final_payment_options_list,
            "api_url": api_url
        })
        payment_transaction.hmac_key = hash_string
        return bbva_tx_values

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'bbva':
            return

        authorization_number = notification_data.get('mp_authorization', '')
        payment_date = pytz.timezone("America/Mexico_City").localize(datetime.strptime(notification_data.get('mp_date'), "%Y-%m-%d %H:%M:%S.%f"), is_dst=None).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        datetime.strptime(datetime.strptime(notification_data.get('mp_date'), "%Y-%m-%d %H:%M:%S.%f").astimezone(
            pytz.timezone('America/Mexico_City')).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        # datetime.now().astimezone(pytz.timezone('America/Mexico_City'))
        received_order = notification_data.get('mp_order')
        received_reference = notification_data.get('mp_reference')
        received_amount = notification_data.get('mp_amount')
        received_authorization = notification_data.get('mp_authorization')
        secret_key = self.provider_id.secret_key
        concate_key = f"""{received_order}{received_reference}{received_amount}{received_authorization}"""
        hash_string = hmac.new(secret_key.encode(), concate_key.encode(), sha256).hexdigest()
        card_type = self.env.ref("l10n_mx_edi.payment_method_tarjeta_de_credito").id if notification_data.get('mp_cardType') == 'C' else self.env.ref("l10n_mx_edi.payment_method_tarjeta_debito").id
        so_id = self.sale_order_ids
        if authorization_number and authorization_number != '000000':

            self.provider_reference = notification_data.get('mp_trx_historyid')

            approved = 'approved' if hmac.compare_digest(notification_data.get('mp_signature'), hash_string) else 'pending'

            if so_id:
                self.sale_data(so_id,notification_data,payment_date,approved,hash_string,card_type)

            if approved == 'approved':
                self._set_done()
        else:  # 'failure'
            # See https://www.payumoney.com/pdf/PayUMoney-Technical-Integration-Document.pdf
            # error_code = notification_data.get('Error')
            if so_id:
                approved = 'refused'
                self.sale_data(so_id, notification_data, payment_date, approved, hash_string, card_type)

            self._set_error(
                "BBVA: " + _("The payment encountered an error with code %s", authorization_number)
            )

    def _get_tx_from_notification_data(self, provider_code, notification_data):

        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'bbva' or len(tx) == 1:
            return tx

        reference = notification_data.get('mp_reference')
        authorization_number = notification_data.get('mp_authorization', '')
        if not reference:
            raise ValidationError(
                "PayUmoney: " + _("Received data with missing reference (%s)", reference)
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'bbva')])
        if not tx:
            raise ValidationError(
                "PayUmoney: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def sale_data(self,so_id,notification_data,payment_date,approved,hash_string,card_type):
        so_id.write({
            'payment_reference': notification_data.get('mp_reference', ''),
            'payment_date': payment_date,
            'payment_method': notification_data.get('mp_paymentMethodcomplete',''),
            'card_holder_name': notification_data.get('mp_cardholdername',''),
            'card_number': f"************{notification_data.get('mp_pan')[-4:]}",
            'authorization': notification_data.get('mp_authorization',''),
            'installments': notification_data.get('mp_promo_msi',''),
            'payment_state': approved,
            'hmac_created_without_authorization': self.hmac_key,
            'hmac_created': hash_string,
            'hmac_received': notification_data.get('mp_signature',''),
            'payment_folio': notification_data.get('mp_trx_historyidComplete',''),
            'folio': notification_data.get('mp_order',''),
            'l10n_mx_edi_payment_method_id': card_type
        })


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """
        If payment received from the BBVA Pago and sale order was confirmed then lock the sale orders.
        """
        res = super(AccountPayment, self).action_post()
        if self.payment_transaction_id and self.payment_transaction_id.provider_id.id == self.env.ref(
                'setu_payment_bbva.payment_provider_bbva').id:
            so = self.payment_transaction_id.sale_order_ids
            for sale_order in so:
                if sale_order and sale_order.state == 'sale':
                    sale_order.action_done()
                    _logger.info(f"BBVA({sale_order.name} -Action done")
        return res
