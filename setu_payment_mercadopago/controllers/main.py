# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
import pprint
from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger("mercado_pago_payment_provider")


# class WebsiteSaleMercadoPago(WebsiteSale):

    # def _get_shop_payment_values(self, order, **kwargs):
    #     """
    #         Authour:udit@setconsulting.com
    #         Date: 17/05/23
    #         Task: 16 Migration
    #         Purpose: If selected pricelist is not available in the monthly installments of Mercado Pago payments acquirers,
    #                     Then remove Mercado Pago from the Payment page.
    #     """
    #     res = super(WebsiteSaleMercadoPago, self)._get_shop_payment_values(order=order, **kwargs)
    #     curr_website_so_pricelist_id = request.website.sale_get_order().pricelist_id.id
    #     mercadopago_acq_obj = request.env.ref('payment.payment_provider_mercado_pago').sudo()
    #     if curr_website_so_pricelist_id and mercadopago_acq_obj.enable_monthly_installment:
    #         prlist_avil_in_installments = mercadopago_acq_obj.monthly_installment_ids.filtered(
    #             lambda month_inst: month_inst.pricelist_id.id == curr_website_so_pricelist_id)
    #         if (mercadopago_acq_obj in res.get('providers')) and not prlist_avil_in_installments:
    #             res.update({'providers': res.get('providers').filtered(lambda p: p.id != mercadopago_acq_obj.id)})
    #     return res


class MercadoPagoController(http.Controller):

    @http.route('/payment/mercado_pago/get_provider_info', type='json', auth='public')
    def mercado_pago_get_provider_info(self, provider_id):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 02/04/25
            Task: 18 Migration
            Purpose: Return provider state, access token and public key when select the payment provider.
        """
        provider_sudo = request.env['payment.provider'].sudo().browse(provider_id).exists()
        return {
            'state': provider_sudo.state,
            'mp_access_token': provider_sudo.mercado_pago_access_token,
            'mp_public_key': provider_sudo.mercadopago_public_key,
        }

    @http.route('/payment/mercado_pago/payment', type='json', auth='public')
    def mercadopago_payment(self, **kwargs):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 02/04/25
            Task: 18 Migration
            Purpose: It will generate the payment token also register customer's payment on the Mercado Pago platform.
        """
        reference = kwargs.get('reference')
        tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        kwargs.update({'mp_payment_transaction': tx_sudo})

        # Creates Payment token
        payment_token_res = request.env['payment.provider'].sudo().browse(
            kwargs.get('provider_id')).mercadopago_s2s_form_process(kwargs)
        _logger.info(f"MercadoPago({kwargs.get('reference') or None}) -payment token data ==> {payment_token_res}")
        if payment_token_res.get('error'):
            return payment_token_res
        else:
            tx_sudo.update({'token_id': payment_token_res.get('success')})

            # Register payment ins Mercado Pago
            mp_payment_res = tx_sudo.mercadopago_s2s_do_transaction(payment_token_res.get('data'))
            res = {
                'result': True,
            }
        return res
