import json

from odoo import http
from odoo.http import request
import requests

import logging
_logger = logging.getLogger(__name__)
from odoo.fields import Command
from odoo.http import request, route
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.account_payment.controllers import portal

from odoo.addons.account.controllers import portal
from odoo.addons.payment.controllers.portal import PaymentPortal
import stripe

class StripeInstallments(payment_portal.PaymentPortal):

    @route("/setu_payment_acqirers/get_installment_plan", type='json', auth='user')
    def get_instalment_count(self, **kw):
        """
                 Authour:sagar.pandya@setconsulting.com
                 Date: 11/04/25
                 Task: Migration v16 to v18
                 Purpose: 1) find installment month pricelist
                          2) check created intent have available plans or not
                 return: installment month

        """
        custom_create_values = {}
        order = request.env["sale.order"].sudo().browse(request.session.get("sale_order_id"))
        if order:
            custom_create_values.update({'sale_order_ids': [(4, order.id)]})
        record_id = order

        invoice_id = False
        landing_route =  kw.get('landing_route').split('/')
        # new_landing_route = False
        if landing_route[2] == 'invoices':
            invoice_id = kw.get('landing_route').split('/')[3].split('?')[0]
            # new_landing_route = kw.get('landing_route')
            if invoice_id:
                invoice_id = request.env['account.move'].sudo().browse(int(invoice_id))
                if invoice_id:
                    custom_create_values.update({'invoice_ids': [(4, invoice_id.id)]})
                    record_id = invoice_id
                    if not order:
                        order = invoice_id.sudo().invoice_line_ids.sale_line_ids.order_id
        if order:
            kw.update({'amount': order.amount_total})
        tx_sudo = record_id.transaction_ids.filtered(lambda tx: tx.payment_intent and tx.state == 'draft')
        tx_sudo = tx_sudo[:1]
        if not tx_sudo and (order or invoice_id):
            tx_sudo = self._create_transaction(
                custom_create_values=custom_create_values, **kw,
            )
            tx_sudo._stripe_create_payment_intent()
        payment_intent = tx_sudo.payment_intent

        available_plans = False
        if tx_sudo and order:
            available_plans = tx_sudo.provider_id.monthly_installment_ids.filtered(
                lambda ml: ml.pricelist_id == order.pricelist_id)
                # available_plans always count 1 as per pricelist
        stripe.api_key = tx_sudo.provider_id.stripe_secret_key

        intent = stripe.PaymentIntent.retrieve(payment_intent)

        confirm_response = False
        months = False
        error = "No Available Plans"
        if method_option:= intent.get('payment_method_options'):
            if method_option.get('card'):
                response_available_plans = method_option.get('card')['installments'].get('available_plans')
                if len(response_available_plans) > 0:
                    response_plan_list =  list(map(lambda item: item.get("count"), response_available_plans))
                    if available_plans:
                        if available_plans.months in response_plan_list:
                            months = available_plans.months
                else:
                    # if small amount then no available plans
                    return {'success': True, 'installment': False}


        if months:
            return {'success': True, 'month': months}
        else:
            return {'error': {'message': error}}


    @staticmethod
    def _validate_transaction_kwargs(kwargs, additional_allowed_keys=()):
        """
             Authour:sagar.pandya@setconsulting.com
             Date: 21/04/25
             Task: Migration v16 to v18
             Purpose: Verify that the keys of a transaction route's kwargs are all whitelisted.
             add payment_method_created key in whitelist.
          """
        # add if condition for installmen plans
        additional = ()
        if kwargs.get('payment_method_created'):
            additional += ('payment_method_created',)
        if kwargs.get('is_payment_voucher_warning'):
            additional += ('is_payment_voucher_warning',)
        res = payment_portal.PaymentPortal._validate_transaction_kwargs(kwargs, additional_allowed_keys = additional)
        return res

    def _create_transaction(self, *args, **kwargs):
        """
           Authour:sagar.pandya@setconsulting.com
           Date: 21/04/25
           Task: Migration v16 to v18
           Purpose: to save created stripe payment method in transaction
        """
        tx_sudo = super()._create_transaction(
            *args, **kwargs
        )
        if created_pm := kwargs.get('payment_method_created'):
            tx_sudo.stripe_payment_method = created_pm
        return tx_sudo




class PortalAccount(portal.PortalAccount, PaymentPortal):

    def _get_common_page_view_values(self, invoices_data, access_token=None, **kwargs):
        """
                Authour:sagar.pandya@setconsulting.com
                Date: 07/04/25
                Task: Migration v16 to v18
                Purpose: filter provider while payment from invoice without having saleorders.
        """
        values = super()._get_common_page_view_values(invoices_data, access_token=access_token, **kwargs)
        stripe_provider_id = request.env.ref('payment.payment_provider_stripe')
        mercadopago_provider_id = request.env.ref('payment.payment_provider_mercado_pago')
        availability_report = values.get('availability_report')
        provider_ids = values.get('providers_sudo')
        if not provider_ids:
            return values
        not_consider_providers = []
        filter_provider = False
        if not invoices_data.get('payment_reference') and invoices_data.get('transaction_route') !='/invoice/transaction/overdue':
            invoice = invoices_data.get('transaction_route').split('/')
            if invoice[1] == 'invoice':
                invoice= invoice[3]

                invoice_id = request.env['account.move'].search([('id','=',int(invoice))])
                if invoice_id and not invoice_id.sudo().invoice_line_ids.sale_line_ids.order_id:
                    filter_provider = True
        else:
            # for overdue invoice (batch payment) - always filter provider
            filter_provider = True

        if filter_provider:
            if stripe_provider_id:
                not_consider_providers.append(stripe_provider_id.id)
                if stripe_provider_id in list(availability_report.get('providers').keys()):
                    availability_report.get('providers').get(stripe_provider_id)['available'] = False

            if mercadopago_provider_id:
                not_consider_providers.append(mercadopago_provider_id.id)
                if mercadopago_provider_id in list(availability_report.get('providers').keys()):
                    availability_report.get('providers').get(mercadopago_provider_id)['available'] = False

            providers_sudo = provider_ids and provider_ids.filtered(
                lambda provider: provider.id not in not_consider_providers)

            logged_in = not request.env.user._is_public()
            partner_sudo = request.env.user.partner_id if logged_in else invoices_data['partner']

            # In sudo mode to read the fields of providers and partner (if logged out).
            payment_methods_sudo = request.env['payment.method'].sudo()._get_compatible_payment_methods(
                providers_sudo.ids,
                partner_sudo.id,
                currency_id=invoices_data['currency'].id,
                report=availability_report,
            )  # In sudo mode to read the fields of providers.
            tokens_sudo = request.env['payment.token'].sudo()._get_available_tokens(
                providers_sudo.ids, partner_sudo.id
            )  # In sudo mode to read the partner's tokens (if logged out) and provider fields.

            payment_form_values = {
                'show_tokenize_input_mapping': PaymentPortal._compute_show_tokenize_input_mapping(
                    providers_sudo
                ),
            }

            values['payment_methods_sudo'] = payment_methods_sudo
            values['providers_sudo'] = providers_sudo
            values['tokens_sudo'] = tokens_sudo
            values['payment_form_values'] = payment_form_values
            values['availability_report'] = availability_report

            _logger.info(f"filter providers")
        return values

