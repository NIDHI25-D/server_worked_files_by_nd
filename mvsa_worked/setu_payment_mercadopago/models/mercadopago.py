# -*- coding: utf-'8' "-*-"

from odoo import osv, fields, models, api, _
import mercadopago
import logging
import pprint

_logger = logging.getLogger(__name__)


class AcquirerMercadopago(models.Model):
    _inherit = 'payment.provider'

    mercadopago_public_key = fields.Char('MercadoPago Public key', size=256)
    mercadopago_access_token = fields.Char('MercadoPago Access token', size=256)
    mercadopago_client_id = fields.Char('MercadoPago Client Id', size=256)
    mercadopago_secret_key = fields.Char('MercadoPago Secret Key', size=256)
    code = fields.Selection(
        selection_add=[('mercadopago', "Mercadopago Do Not Use")],
        ondelete={'mercadopago': 'set default'})


    def find_mercado_pago_regi_customner(self, data, provider_id):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 02/04/25
            Task: 18 Migration
            Purpose: It will find the customer on the Mercado Pago platform if not found then registered it
                    and return the Mercado Pago customer id
        """
        provider_id = self.env['payment.provider'].browse(provider_id)
        sdk = mercadopago.SDK(provider_id.mercado_pago_access_token)
        transaction_id = data.get('mp_payment_transaction')
        partner_id = self.env['res.partner'].browse(data.get('partner_id'))
        invoice_ids = transaction_id.invoice_ids
        filters = {"email": partner_id.email}
        if provider_id.state == 'test':
            filters = {"email": "test_payer_11445@testuser.com"}
        _logger.info(f"MercadoPago({data.get('reference')}) -filters :- {filters}")
        customers_response = sdk.customer().search(filters=filters)
        _logger.info(f"MercadoPago({data.get('reference')})- Customers Response :- {customers_response}")
        if customers_response['status'] == 200:
            if customers_response['response']['results']:
                regi_cust_id = customers_response['response']['results'][0]['id']
                if regi_cust_id:
                    return regi_cust_id
                    # Register customer into the Mercadopago website
        customer_data = {
            "email": transaction_id.sale_order_ids.partner_id.email if not invoice_ids else invoice_ids.partner_id.email,
            "first_name": data.get('website_order_partner_name', partner_id.name),
        }
        _logger.info(f"MercadoPago({data.get('reference')}) -New Customer data :- {customer_data}")
        customer_new = sdk.customer().create(customer_data)
        _logger.info(f"MercadoPago({data.get('reference')}) - New Customer creatings response :- {customer_new}")
        if customer_new['status'] == 201:
            regi_cust_id = customer_new['response']['id']
            if regi_cust_id:
                return regi_cust_id
        else:
            return {"error": f"{customer_new.get('response', {}).get('cause', [{}])[0].get('description')}"}
        return False

    def mercadopago_s2s_form_process(self, data):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 02/04/25
            Task: 18 Migration
            purpose :   1) find or register customer on pago platform
                        2) create payment token if save payment details is selected
                        3) check the installments condition with the order amount
                        4) update applied_installment_id as installment id in odoo

            notes: tokenization_request_allowed from save payment details
        """
        mercadopago_customer_id = self.find_mercado_pago_regi_customner(data, data['provider_id'])
        _logger.info(
            f"MercadoPago({data.get('reference')}) - Get customer from MP server :- {mercadopago_customer_id}")
        if isinstance(mercadopago_customer_id, dict):
            return mercadopago_customer_id
        tx_sudo = data.get('mp_payment_transaction')

        if data.get('tokenization_request_allowed'):
            payment_token = self.env['payment.token'].sudo().create({
                'provider_ref': mercadopago_customer_id,
                'provider_id': data['provider_id'],
                'partner_id': data['partner_id'],
                'mercadopago_cards_token': data.get('mp_payment_token').get('id'),
                'payment_method_id':tx_sudo.payment_method_id.id
            })
        else:
            data.update({
                'provider_ref': mercadopago_customer_id,
                'provider_id': data['provider_id'],
                'partner_id': data['partner_id'],
                'mercadopago_cards_token': data.get('mp_payment_token').get('id'),
            })

        # payment_details fields needs tobes adds ins boves token

        temp_payment_methods_data = data.get('mp_payment_method_data').get('results')[0] if data.get(
            'mp_payment_method_data').get('results') else None
        _logger.info(
            f"MercadoPago({data.get('reference')}) - Cards validation response from the Mercado pagoes :-{temp_payment_methods_data}")
        if temp_payment_methods_data:

            if data.get('tokenization_request_allowed') and payment_token:
                payment_token.update({
                    'mercadopago_payment_method': temp_payment_methods_data.get('id'),
                    'mercadopago_card_issuer_name': temp_payment_methods_data.get('issuer').get('name'),
                    'mercadopago_card_issuer_id': temp_payment_methods_data.get('issuer').get('id'),
                    'mercadopago_payment_type_name': temp_payment_methods_data.get('payment_type_id'),
                })
            else:
                data.update({
                    'mercadopago_payment_method': temp_payment_methods_data.get('id'),
                    'mercadopago_card_issuer_name': temp_payment_methods_data.get('issuer').get('name'),
                    'mercadopago_card_issuer_id': temp_payment_methods_data.get('issuer').get('id'),
                    'mercadopago_payment_type_name': temp_payment_methods_data.get('payment_type_id'),
                })

        if tx_sudo.sale_order_ids:
            if self.env['ir.module.module'].search([('name', '=', 'setu_payment_acqirers'), ('state', '=', 'installed')]):
                if self.enable_monthly_installment and self.sudo().monthly_installment_ids:
                    selected_pricelist_id = data.get('mp_payment_transaction').sale_order_ids.pricelist_id.id
                    if selected_pricelist_id in self.sudo().monthly_installment_ids.mapped('pricelist_id').ids:
                        applyied_installment_id = self.sudo().monthly_installment_ids.filtered(
                            lambda inst: inst.pricelist_id.id == selected_pricelist_id)
                        if data.get('tokenization_request_allowed') and payment_token:
                            payment_token.update({
                                'applied_installment_id': applyied_installment_id.id,
                            })
                        else:
                            data.update({
                                'applied_installment_id': applyied_installment_id.id,
                            })
                    curr_website_so_pricelist_id = data.get('mp_payment_transaction').sale_order_ids.pricelist_id.id
                    if curr_website_so_pricelist_id:
                        _logger.info(
                            f"MercadoPago({data.get('reference')}) - curr_website_so_pricelist_id :- {curr_website_so_pricelist_id}")
                        selected_installments_months = self.sudo().monthly_installment_ids.filtered(
                            lambda month_inst: month_inst.pricelist_id.id == curr_website_so_pricelist_id).months
                        result = list(
                            filter(lambda installments: installments.get('installments') == selected_installments_months,
                                   data.get('mp_payment_method_data').get('results')[0].get('payer_costs')))
                        if result:
                            so_amount = data.get('mp_payment_transaction').sale_order_ids.amount_total
                            if so_amount < result[0].get('min_allowed_amount') or so_amount > result[0].get(
                                    'max_allowed_amount'):
                                error_msg = ""
                                if so_amount < result[0].get('min_allowed_amount'):
                                    error_msg += f"{selected_installments_months}-months Installments must required minimum order amounts {result[0].get('min_allowed_amount')} MXN"
                                else:
                                    error_msg += f"{selected_installments_months}-months Installments must required maximum order amount {result[0].get('max_allowed_amount')} MXN"
                                    _logger.info(f"MercadoPago({data.get('reference')}) -mercadopago_s2s_form_process error ==>{temp_payment_methods_data}")
                                return {"error": error_msg}
                        else:
                            return {
                                "error": f"This card not supported {selected_installments_months}-months installments.So,Enter a valid card"
                            }
                        # if temp_payment_methods_data and temp_payment_methods_data.get('deferred_capture') == 'unsupported':
                        #     _logger.info(f"mercadopago_s2s_form_process error ==>{temp_payment_methods_data}")
                        #     return {
                        #         "error": f"This card not supported.Please use another cards"
                        #     }
        return {"success": payment_token if (data.get('tokenization_request_allowed') and payment_token) else False,"data":data}



        # def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        #     providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)
        #     return providers