import logging
from odoo import http, _
from odoo.http import request, route
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import WebsiteSale as websiteSaleController
from odoo.addons.sale.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import ValidationError
import base64
from odoo.tools import str2bool
_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    @http.route(
        '/shop/address', type='http', auth='public', website=True, sitemap=False, methods=['GET']
    )
    def shop_address(
            self, partner_id=None, address_type='billing', use_delivery_as_billing=None, **query_params
    ):
        partner_id = partner_id and int(partner_id)
        use_delivery_as_billing = str2bool(use_delivery_as_billing or 'false')
        order_sudo = request.website.sale_get_order()

        if redirection := self._check_cart(order_sudo):
            return redirection

        # Retrieve the partner whose address to update, if any, and its address type.
        partner_sudo, address_type = self._prepare_address_update(
            order_sudo, partner_id=partner_id, address_type=address_type
        )
        if not partner_sudo and address_type == 'delivery':
            return request.redirect('/my/manage-address?steps=4')
        if partner_sudo:  # If editing an existing partner.
            use_delivery_as_billing = (
                    order_sudo.partner_shipping_id == order_sudo.partner_invoice_id
            )

        # Render the address form.
        address_form_values = self._prepare_address_form_values(
            order_sudo,
            partner_sudo,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            **query_params
        )
        return request.render('website_sale.address', address_form_values)

    @route(
        '/shop/checkout', type='http', methods=['POST'], auth='public', website=True, sitemap=False
    )
    def shop_checkout(self, try_skip_step=None, **query_params):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: override the method and Sending in our controller
        """
        order_sudo = request.website.sale_get_order()
        request.session['sale_last_order_id'] = order_sudo.id
        try_skip_step = str2bool(try_skip_step or 'false')
        can_skip_delivery = True
        if order_sudo._has_deliverable_products():
            can_skip_delivery = False

        if try_skip_step and can_skip_delivery:
            invoice_partner_sudo = order_sudo.partner_invoice_id
            if (
                    not self._check_billing_address(invoice_partner_sudo)
                    and invoice_partner_sudo._can_be_edited_by_current_customer(order_sudo, 'billing')
            ):
                return request.redirect('/my/manage-address')

            delivery_partner_sudo = order_sudo.partner_shipping_id
            if (
                    not order_sudo.only_services
                    and not self._check_delivery_address(delivery_partner_sudo)
                    and delivery_partner_sudo._can_be_edited_by_current_customer(order_sudo, 'delivery')
            ):
                return request.redirect('/my/manage-address')
            else:
                return super(WebsiteSale, self).shop_checkout(try_skip_step, **query_params)
        if query_params.get('xhr'):
            if order_sudo.partner_id.id == request.website.user_id.sudo().partner_id.id:
                return request.redirect('/shop/address')

            self._prepare_checkout_page_values(order_sudo, **query_params)
            return request.redirect('/my/manage-address?steps=4')
        else:
            return request.redirect('/my/manage-address')


    def _prepare_checkout_page_values(self, order_sudo, **query_params):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: need to called this in 18 as there are changes we needs is removed from the main method (partner_shipping_id related).
        """
        order_sudo = request.website.sale_get_order(force_create=True)
        res = super()._prepare_checkout_page_values(order_sudo, **query_params)
        if res.get('delivery_addresses', False):
            if query_params.get('partner_id') or 'use_billing' in query_params:
                if 'use_billing' in query_params:
                    partner_id = order_sudo.partner_id.id
                else:
                    partner_id = int(query_params.get('partner_id'))
                if partner_id in res.get('delivery_addresses', False).mapped('id'):
                    order_sudo.partner_shipping_id = partner_id
        return res

    def _check_addresses(self, order_sudo):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: Check the any fields value missing or not and send as per the requested url
        """
        # Check Billing Address Mandatory Fields and redirect to step 3 of manage-address form
        invoice_partner_sudo = order_sudo.partner_invoice_id
        if (
                not self._check_billing_address(invoice_partner_sudo)
                and invoice_partner_sudo._can_be_edited_by_current_customer(order_sudo, 'billing')
        ):
            return request.redirect('/my/manage-address?steps=3?&error=1')
        # Check Shipping Address Mandatory Fields and redirect to step 4 of manage-address form
        delivery_partner_sudo = order_sudo.partner_shipping_id
        if (
                not order_sudo.only_services
                and not self._check_delivery_address(delivery_partner_sudo)
                and delivery_partner_sudo._can_be_edited_by_current_customer(order_sudo, 'delivery')
        ):
            return request.redirect('/my/manage-address?steps=4?&error=1')

    @route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: check the condition and send as per the url
        """
        if not request.env.user.partner_id.is_company_data:
            return request.redirect('../my/manage-address?steps=2')
        else:
            return super(WebsiteSale,self).shop_payment(**post)

class CheckoutExtended(http.Controller):
    @http.route(['/my/manage-address'], type='http', auth="user", website=True, sitemap=False)
    def manage_address(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: Create a new template for the new customers
        """
        countries = request.env['res.country'].search([])
        order = request.website.sale_get_order()
        request.session['sale_last_order_id'] = order.id
        Contacts = request.env['res.partner'].sudo().search(
            [('id', '!=', request.env.user.partner_id.id),
             ('parent_id', '=', request.env.user.partner_id.parent_id.id)])
        values = {
            'countries': countries,
            'country_states': countries.mapped('state_ids'),
            'country': request.env['res.users'].search([('id', '=', request.env.user.id)]).country_id,
            'partner_sudo': request.env.user.partner_id,
            'user_id': request.env['res.users'].search([('id', '=', request.env.user.id)]),
            'data': Contacts,
        }
        return request.render("setu_ecommerce_checkout_extended.manage_address", values)

    @http.route(['/my/manage-address/account'], type='http', auth="public", website=True, sitemap=False, csrf=False)
    def account_infomration(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: Save all details of new registered company and customers via steps.
        """
        # Prepare context for no_vat_validation
        context = dict(request.context)
        context['no_vat_validation'] = True
        request.update_context(**context)
        # Prepare First Step (account) Information
        if post.get('step') == "account_info":
            name = post.get('name')
            email = post.get('email')
            phone = post.get('phone')
            request.env.user.partner_id.write({
                'name': name,
                'email': email,
                'phone': phone,
                'type': 'other',
            })
        # Prepare Second Step (company) Information
        if post.get('step') == "company_info":
            rfc = post.get('rfc')
            company = False
            is_invoice_required = post.get('required_invoice')
            tax_position = post.get('tax_position')
            use_of_cfdi = post.get('use_of_cfdi')
            to_define = post.get('to_define')
            if is_invoice_required == 'on' and not request.env.user.partner_id.is_company_user:
                request.env.user.partner_id.is_required_invoice = True
                request.website.sale_get_order().fiscal_position_id = int(tax_position)
                request.website.sale_get_order().l10n_mx_edi_usage = use_of_cfdi
                request.website.sale_get_order().l10n_mx_edi_payment_method_id = int(to_define)
                request.env.user.partner_id.fiscal_position_id = int(tax_position)
                request.env.user.partner_id.l10n_mx_edi_usage = use_of_cfdi
                request.env.user.partner_id.l10n_mx_edi_payment_method_id = int(to_define)
                if not request.env.user.partner_id.company_type == 'company':
                    if rfc:
                        company = request.env['res.partner'].sudo().search([('vat', '=', rfc)]).filtered(
                            lambda x: x.company_type == 'company')
                        if len(company) > 1:
                            company = company[0]
                    if rfc and not company:
                        company = request.env['res.partner'].sudo().create({
                            'name': post.get('company_name'),
                            'vat': post.get('rfc'),
                            'company_type': 'company',
                            'email': request.env.user.partner_id.email,
                            'is_consume_loyalty_points': True,
                            'is_budgets_permission': True,
                            'is_sale_orders_permission': True,
                            'is_purchase_permission': True,
                            'is_invoices_permission': True,
                            'is_claims_permission': True,
                            'is_company_user': True,
                            'fiscal_position_id': int(tax_position),
                            'l10n_mx_edi_usage': use_of_cfdi,
                            'l10n_mx_edi_payment_method_id': int(to_define),
                            'hcategory_id': request.website.hcategory_id.id
                        })
                        request.env.user.partner_id.sudo().write({
                            'is_main_partner': True,
                            'is_owner': True,
                            'is_consume_loyalty_points': True,
                            'is_budgets_permission': True,
                            'is_sale_orders_permission': True,
                            'is_purchase_permission': True,
                            'is_invoices_permission': True,
                            'is_claims_permission': True,
                            'is_company_user': True,
                        })
                    request.env.user.partner_id.sudo().write({
                        'parent_id': company,
                    })
                    request.env.user.partner_id.is_company_data = True
                    request.env.user.partner_id.sudo().setu_company_type = post.get('setu_company_type')
                    if request.env.user.partner_id.parent_id:
                        request.env.user.partner_id.parent_id.sudo().setu_company_type = post.get('setu_company_type')
                    return request.render("setu_ecommerce_checkout_extended.form_details",
                                          {'company_name': company.name})
                else:
                    request.env.user.partner_id.write({
                        'vat': post.get('rfc') if post.get('rfc') else '',
                        'name': post.get('company_name') if post.get('company_name') else '',
                    })
                    request.env.user.partner_id.is_company_data = True
            else:
                if request.env.user.partner_id.parent_id:
                    request.website.sale_get_order().fiscal_position_id = request.env.user.partner_id.parent_id.fiscal_position_id
                    request.website.sale_get_order().l10n_mx_edi_usage = request.env.user.partner_id.parent_id.l10n_mx_edi_usage
                    request.website.sale_get_order().l10n_mx_edi_payment_method_id = request.env.user.partner_id.parent_id.l10n_mx_edi_payment_method_id
                    request.env.user.partner_id.fiscal_position_id = request.env.user.partner_id.parent_id.fiscal_position_id
                    request.env.user.partner_id.l10n_mx_edi_usage = request.env.user.partner_id.parent_id.l10n_mx_edi_usage
                    request.env.user.partner_id.l10n_mx_edi_payment_method_id = request.env.user.partner_id.parent_id.l10n_mx_edi_payment_method_id
                    request.env.user.partner_id.write({
                        'street': request.env.user.partner_id.parent_id.street,
                        'street2': request.env.user.partner_id.parent_id.street2,
                        'zip': request.env.user.partner_id.parent_id.zip,
                        'country_id': request.env.user.partner_id.parent_id.country_id.id,
                        'state_id': request.env.user.partner_id.parent_id.state_id.id,
                        'l10n_mx_edi_colony': request.env.user.partner_id.parent_id.l10n_mx_edi_colony,
                        'city': request.env.user.partner_id.parent_id.city,
                    })
                else:
                    if not request.env.user.partner_id.is_company_user:
                        website_dummy_user_id = request.env.ref(
                            'setu_ecommerce_checkout_extended.website_dummy_user').sudo()
                        data = website_dummy_user_id.read()[0]
                        data.pop('name')
                        data.pop('id')
                        data.pop('email')
                        data.pop('active')
                        data.pop('mobile')
                        data.pop('phone')
                        data.pop('barcode')
                        data['country_id'] = data.get('country_id')[0] if 'country_id' in data else False
                        request.env.user.partner_id.write(data)
                        request.env.user.partner_id.write({
                            'zip': website_dummy_user_id.postal_code_id.postal_code,
                            'city': website_dummy_user_id.postal_code_id.city_id.name
                        })
            request.env.user.partner_id.is_company_data = True
        # Prepare Third Step (billing) Information
        if post.get('step') == "billing_info":
            postal_code = post.get('postal_code')
            street_and_number = post.get('street_and_number')
            street2 = post.get('street2')
            country_id = post.get('country_id')
            states_id = post.get('country_states_id')

            # Add sepomex Colony If post.get('colony_text')
            if not post.get('readonly') == 'True':
                if request.env.user.partner_id.parent_id.company_type == 'company':
                    request.env.user.partner_id.parent_id.write({
                        'street': street_and_number,
                        'street2': street2,
                        'zip': postal_code,
                        'country_id': int(country_id),
                        'state_id': int(states_id) if states_id else None,
                        'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get('colony_text'),
                        'city': post.get('city'),
                    })
                    request.env.user.partner_id.write({
                        'street': street_and_number,
                        'street2': street2,
                        'zip': postal_code,
                        'country_id': int(country_id),
                        'state_id': int(states_id) if states_id else None,
                        'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get('colony_text'),
                        'city': post.get('city'),
                    })
                else:
                    request.env.user.partner_id.write({
                        'street': street_and_number,
                        'street2': street2,
                        'zip': postal_code,
                        'country_id': int(country_id),
                        'state_id': int(states_id) if states_id else None,
                        'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get('colony_text'),
                        'city': post.get('city'),
                    })
            else:
                request.env.user.partner_id.write({
                    'street': street_and_number,
                    'street2': street2,
                    'zip': postal_code,
                    'country_id': request.env.user.partner_id.parent_id.country_id.id if request.env.user.partner_id.parent_id else request.env.user.partner_id.country_id.id,
                    'state_id': request.env.user.partner_id.parent_id.state_id.id if request.env.user.partner_id.parent_id else request.env.user.partner_id.state_id.id,
                    'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get('colony_text'),
                    'city': post.get('city'),
                })
        # Prepare Fourth Step (shipping) Information
        if post.get('step') == "shipping_info":
            email = post.get('email')
            phone = post.get('phone')
            if post.get('shipping_partner_id') == 'shipping_partner_id':
                request.env['res.partner'].sudo().create(
                    {'name': post.get('name'), 'street': post.get('street_and_number'),
                     'street2': post.get('street2'),
                     'type': 'delivery',
                     'zip': post.get('postal_code'),
                     'country_id': int(post.get('country_id')),
                     'state_id': int(post.get('country_states_id')) if (
                         post.get('country_states_id')) else None,
                     'email': email,
                     'city': post.get('city'),
                     'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get(
                         'shipping_colony_text'),
                     'phone': post.get('phone'),
                     'parent_id': request.env.user.partner_id.id,
                     })
                return request.redirect('/shop/payment')
            else:
                partner_id = request.env['res.partner'].browse(int(post.get('shipping_partner_id')))
                partner_id.sudo().update({
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'phone': post.get('phone'),
                    'zip': post.get('postal_code'),
                    'city': post.get('city'),
                    'street': post.get('street_and_number'),
                    'street2': post.get('street2'),
                    'country_id': int(post.get('country_id')),
                    'l10n_mx_edi_colony': post.get('colony') if post.get('colony') else post.get(
                        'shipping_colony_text'),
                    'state_id': int(post.get('country_states_id')) if (post.get('country_states_id')) else None,
                })
        # Delete Address From Partner Child's
        if post.get('delete_address'):
            request.env.user.partner_id.child_ids.search([('id', '=', int(post.get('partner_id')))]).active = False

    @http.route(['/my/manage-address/account/colony'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def get_colony_data(self, zip_code, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: Fetch all colony details from sepomex as per the zip code entered by customer.
            return : dictionary the of the details of the contact from the zip code as per the matches from the sepomex.
        """
        colony_ids = request.env['sepomex.res.colony'].sudo().search([('postal_code', '=', zip_code)])
        city = colony_ids.city_id.name
        a = "<option value='"
        b = "'>"
        c = "</option>"
        colony_selection_string, state_selection_string = "", ""
        for colony in colony_ids:
            temp = a + str(colony.name) + b + colony.name + c
            colony_selection_string += temp
        colonys = []
        for colony in colony_ids:
            colonys.append(colony.name)
        for states in colony_ids.city_id.country_id.state_ids:
            temp = a + str(states.id) + b + states.name + c
            state_selection_string += temp

        return {'city': city if city else '', 'colony': colony_selection_string, 'colony_text': colonys,
                'country_id': colony_ids.city_id.country_id.id, 'state_id': colony_ids.city_id.state_id.id,
                'state_ids': state_selection_string}

    @http.route(['/my/manage-address/account/edit_address'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def get_edit_address_data(self, partner_id, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: edit the information of the customer.
        """
        partner_id = request.env['res.partner'].browse(int(partner_id))
        a = "<option value='"
        b = "'>"
        c = "</option>"
        colony_selection_string = ""
        for colony in request.env['sepomex.res.colony'].sudo().search([('postal_code', '=', partner_id.zip)]):
            if partner_id.l10n_mx_edi_colony == colony.name:
                temp = "<option value='" + colony.name + "' selected>" + colony.name + "</option>"
            else:
                temp = a + str(colony.name) + b + colony.name + c
            colony_selection_string += temp
        return {
            'partner_id': partner_id.id,
            'city': partner_id.city,
            'colony': partner_id.l10n_mx_edi_colony if partner_id.l10n_mx_edi_colony else '',
            'name': partner_id.name if partner_id.name else '',
            'street_number': partner_id.street if partner_id.street else '',
            'phone': partner_id.phone if partner_id.phone else None,
            'street2': partner_id.street2 if partner_id.street2 else '',
            'zip': partner_id.zip if partner_id.zip else None,
            'email': partner_id.email if partner_id.email else '',
            'country_id': partner_id.country_id.id if partner_id.country_id.id else None,
            'state_id': partner_id.state_id.id if partner_id.state_id.id else None,
            'is_colony_selection': True if request.env['sepomex.res.colony'].sudo().search(
                [('name', '=', partner_id.l10n_mx_edi_colony), ('postal_code', '=', partner_id.zip)]) else False,
            'colony_selection_string': colony_selection_string,
        }

    # Generate company name based on rfc in step 2 of checkout form
    @http.route(['/my/manage-address/check_rfc'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def check_rfc(self, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/03/25
            Task: Migration to v18 from v16
            Purpose: Compare vat number for new customers
        """
        rfc = args.get('rfc')
        if rfc:
            company = request.env['res.partner'].sudo().search([('vat', '=', rfc)]).filtered(
                lambda x: x.company_type == 'company')
            if len(company) > 1:
                company = company[0]
            return {'company_name': company.name, 'rfc': rfc, 'company_id': company.id,
                    'setu_company_type': company.setu_company_type}
        else:
            return {'company_name': False, 'rfc': rfc}

    @http.route(['/my/manage-address/request'], type='json', auth="user", website=True, sitemap=False, csrf=False)
    def send_request(self, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/03/25
            Task: Migration to v18 from v16
            Purpose: Sending a mail to the company regarding the new user wants to connect with that company
        """
        partner_id = request.env.user.partner_id
        if not partner_id.requested_company_id:
            try:
                request_company = args.get('partner_id', False)
                if request_company:
                    company = request.env['res.partner'].sudo().search([('id', '=', int(request_company))])
                    partner_id.requested_company_id = company.id
                    request.env.ref(
                        'setu_ecommerce_checkout_extended.email_template_customer_contact_link_request').with_context(
                        request_company=request_company,
                        request_company_name=partner_id.name,
                        email_to=company.email,
                        email_from=request.env.user.partner_id.email,
                        current_company=partner_id.id,
                    ).sudo().send_mail(company.id, force_send=True)
                    return {'message': 'Requested Successful'}
            except MailDeliveryException as exception:
                _logger.error(exception)
                return {'message': exception}
        else:
            return {'alert': 'You Already Requested For Some Company'}

    @http.route(['/my/manage-address/request/<int:company_id>/<int:partner_id>/approve'], type='http', auth="public",
                website=True, sitemap=False, csrf=False)
    def approve_request(self, partner_id, company_id, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/03/25
            Task: Migration to v18 from v16
            Purpose: approve a new user to connect with the requested company and send a confirmation mail
        """
        context = dict(request.context)
        context['no_vat_validation'] = True
        partner_id = request.env['res.partner'].sudo().search([('id', '=', int(partner_id))])
        company_id = request.env['res.partner'].sudo().search([('id', '=', int(company_id))])
        partner_id.parent_id = company_id.id
        partner_id.is_company_data = True
        partner_id.is_company_user = True
        partner_id.is_required_invoice = False
        partner_id.requested_company_id = False
        try:
            request.env.ref(
                'setu_ecommerce_checkout_extended.email_template_customer_contact_link_request_approve').with_context(
                email_to=partner_id.email,
                email_from=company_id.email,
                company_name=company_id.name,
                partner_name=partner_id.name,
            ).sudo().send_mail(partner_id.id, force_send=True)
            return request.redirect('/')
        except MailDeliveryException as exception:
            _logger.error(exception)

    @http.route(['/my/manage-address/request/<int:company_id>/<int:partner_id>/reject'], type='http', auth="public",
                website=True, sitemap=False, csrf=False)
    def reject_request(self, partner_id, company_id, **args):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/03/25
            Task: Migration to v18 from v16
            Purpose: rejects company connection request and send a mail
        """
        context = dict(request.context)
        context['no_vat_validation'] = True
        partner_id = request.env['res.partner'].sudo().search([('id', '=', int(partner_id))])
        company_id = request.env['res.partner'].sudo().search([('id', '=', int(company_id))])
        partner_id.is_company_data = False
        partner_id.is_required_invoice = False
        partner_id.requested_company_id = False
        try:
            request.env.ref(
                'setu_ecommerce_checkout_extended.email_template_customer_contact_link_request_reject').with_context(
                email_to=partner_id.email,
                email_from=company_id.email,
                company_name=company_id.name,
                partner_name=partner_id.name,
            ).sudo().send_mail(partner_id.id, force_send=True)
            return request.redirect('/')
        except MailDeliveryException as exception:
            _logger.error(exception)

class CustomerPortal(portal.CustomerPortal):
    items_per_page = 80

    def _prepare_home_portal_values(self, counters):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: get a count of a contact
        """
        values = super()._prepare_home_portal_values(counters)
        Contacts = request.env['res.partner'].sudo().search(
            [('parent_id', '=', request.env.user.partner_id.parent_id.id)])
        Contacts = Contacts.filtered(lambda x: x.id != request.env.user.partner_id.id)

        if 'contacts_count' in counters:
            values['contacts_count'] = request.env['res.partner'].search_count([('id', 'in', Contacts.ids)]) \
                if Contacts.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/contacts', '/my/contacts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contacts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/03/25
            Task: Migration to v18 from v16
            Purpose: Prepare a contacts related values and view for that
        """
        values = self._prepare_portal_layout_values()
        Contacts = request.env['res.partner'].sudo().search(
            [('parent_id', '=', request.env.user.partner_id.parent_id.id)])
        Contacts = Contacts.filtered(lambda x: x.id != request.env.user.partner_id.id)
        contacts_count = request.env['res.partner'].search_count([('id', '=', Contacts.ids)])

        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=contacts_count,
            page=page,
            step=self._items_per_page
        )

        values.update({
            'date': date_begin,
            'page_name': 'contacts',
            'pager': pager,
            'default_url': '/my/contacts',
            'sortby': sortby,
            'data': Contacts,
            'origin': request.httprequest.path,
        })
        return request.render("setu_ecommerce_checkout_extended.portal_my_contacts_from_portal", values)

    @http.route(['/my/manage-address/delete_person'], type='http', auth="public", website=True, sitemap=False,
                csrf=False)
    def delete_person(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: delete a user and corresponding to it partner.
        """
        if request.env.user.partner_id.child_ids.search([('id', '=', int(post.get('partner_id')))]).user_ids:
            request.env.user.partner_id.child_ids.search(
                [('id', '=', int(post.get('partner_id')))]).user_ids.active = False
            request.env.user.partner_id.child_ids.search([('id', '=', int(post.get('partner_id')))]).active = False

    @http.route(['/my/contacts/add'], type='http', auth="user", website=True)
    def add_contacts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: Prepare a value for create a new contact and set a permissions for that contact.
        """
        values = self._prepare_portal_layout_values()
        values.update({
            'date': date_begin,
            'page_name': 'add_contacts',
            'default_url': '/my/contacts/add',
            'sortby': sortby,
            'origin': kw.get('origin', False),
        })
        return request.render("setu_ecommerce_checkout_extended.add_contacts", values)

    @http.route(['/my/contacts/edit'], type='http', auth="user", website=True)
    def edit_contacts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: Update the details for selected contact
        """
        values = self._prepare_portal_layout_values()
        values.update({
            'date': date_begin,
            'page_name': 'edit_contacts',
            'default_url': '/my/contacts/edit',
            'sortby': sortby,
            'mode': kw.get('mode', False),
            'origin': kw.get('origin', False),
            'partner_id': int(kw.get('partner_id')) if kw.get('partner_id') else False
        })
        return request.render("setu_ecommerce_checkout_extended.add_contacts", values)

    @http.route(['/my/contacts/add_contact_data'], type='http', auth="public", website=True, sitemap=False, csrf=False)
    def add_contact_data(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: create a new contact as per the given permission and also update a contact details.
        """
        context = dict(request.context)
        context['no_vat_validation'] = True
        if post.get('mode') == 'edit':
            user = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])
            user.write({
                'name': post.get('name'),
            })
            user.partner_id.sudo().write({
                'is_consume_loyalty_points': post.get('is_consume_loyalty_points', False),
                'is_budgets_permission': post.get('is_budgets_permission', False),
                'is_sale_orders_permission': post.get('is_sale_orders_permission', False),
                'is_purchase_permission': post.get('is_purchase_permission', False),
                'is_invoices_permission': post.get('is_invoices_permission', False),
                'is_claims_permission': post.get('is_claims_permission', False),
                'is_main_partner': post.get('is_main_partner', False),
            })
            if user and post.get('origin'):
                return request.redirect('/my/contacts')
            if user:
                return request.redirect('/my/manage-address')
            else:
                return request.redirect('/my/contacts/edit')
        else:
            if not request.env['res.users'].sudo().search([('login', '=', post.get('email'))]):
                portal_user = request.env.ref('base.template_portal_user_id').sudo().copy()
                portal_user.active = True
                portal_user.write({
                    'name': post.get('name'),
                    'login': post.get('email')
                })
                partner_id = request.env.user.partner_id
                if request.env.user.partner_id.parent_id and request.env.user.partner_id.is_main_partner:
                    partner_id = request.env.user.partner_id.parent_id
                portal_user.partner_id.sudo().write({
                    'parent_id': partner_id.id,
                    'is_consume_loyalty_points': post.get('is_consume_loyalty_points', False),
                    'is_budgets_permission': post.get('is_budgets_permission', False),
                    'is_sale_orders_permission': post.get('is_sale_orders_permission', False),
                    'is_purchase_permission': post.get('is_purchase_permission', False),
                    'is_invoices_permission': post.get('is_invoices_permission', False),
                    'is_claims_permission': post.get('is_claims_permission', False),
                    'email': post.get('email'),
                    'is_company_data': True,
                    'is_company_user': True
                })

                try:
                    portal_user.with_context(create_user=True).action_reset_password()
                except:
                    portal_user.partner_id.with_context(create_user=True).signup_cancel()
                if portal_user and len(post.get('origin')) > 0:
                    return request.redirect('/my/contacts')
                if portal_user:
                    return request.redirect('/my/manage-address')
                else:
                    return request.redirect('/my/contacts/add')
            else:
                values = ({
                    'error': post.get('email') + ' is already available in our system please use another one.',
                    'mode': 'add',
                    'name': post.get('name'),
                })
                return request.render("setu_ecommerce_checkout_extended.add_contacts", values)


    @http.route(['/portal/upload_attachment'], type='http', auth='user', website=True, method=['POST'])
    def upload_attachment(self, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/03/25
            Task: Migration to v18 from v16
            Purpose: upload attachment at portal --> Attach your Fiscal situation certificate.
        """
        if kw and kw.get('partner'):

            partner = int(kw.get('partner'))
            model = 'res.partner'
            file = kw.get('attach_fiscal_situation_certificate')
            if file:
                if file.filename.split(".")[-1] in ['png', 'jpg', 'jpeg'] or ['mp4', 'mkv', 'webm'] or ['pdf', 'docx', 'txt']:
                    attachment_value = {
                        'name': file.filename,
                        'datas': base64.encodebytes(file.read()),
                        'res_model': model,
                        'res_id': partner,
                    }
                    attachment_obj = request.env['ir.attachment'].sudo()
                    attachment_id = attachment_obj.create(attachment_value)
                    partner_id = request.env['res.partner'].sudo().browse(partner)

                    request.env['mail.message'].sudo().create({
                        'subject': 'Fiscal Situation Certificate',
                        'model': model,
                        'res_id': partner,
                        'attachment_ids': [(6, 0, attachment_id.ids)],
                    })


        return request.redirect('/my')