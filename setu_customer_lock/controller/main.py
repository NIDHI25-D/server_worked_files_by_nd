# -*- coding: utf-8 -*-
import werkzeug
from odoo import fields, http, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route


class SetuCustomerLock(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will not allow restricted customers to do a purchase.
        """

        order = request.website.sale_get_order()

        not_eligible_partner = order.partner_id and order.partner_id.mapped('category_id').filtered(
            lambda x: x.is_customer_lock_reason) or False
        if not not_eligible_partner and order.partner_id and order.partner_id.email:
            customer_email = order.partner_id.email.strip().lower()
            not_eligible_partner = request.env['res.partner'].sudo().search(
                [('email', '=', customer_email)]).mapped(
                'category_id').filtered(
                lambda x: x.is_customer_lock_reason) or False
        if not_eligible_partner:
            request.session['not_elegible_customer_error'] = (
                _("Your user is blocked, please contact the credit and collection area for "
                  "clarification."))
            return request.redirect('/shop')

        return super(SetuCustomerLock, self).shop_payment(**post)

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: set qty during cart update and if not get then through error.
        """
        try:
            set_qty_int = set_qty and int(set_qty) or False
            add_qty_int = add_qty and int(add_qty) or False
        except Exception as e:
            set_qty_int = False
            add_qty_int = False
        if (set_qty_int and set_qty_int > 0) or (add_qty_int and add_qty_int > 0):
            current_user_partner = request.env.user and request.env.user.partner_id or False
            not_eligible_partner = request.website.elegible_customer(current_user_partner)
            if not_eligible_partner:
                request.session['not_elegible_customer_error'] = (
                    _("Your user is blocked, please contact the credit and collection area for "
                      "clarification."))
                return request.redirect(request.httprequest.referrer)
        return super(SetuCustomerLock, self).cart_update(product_id, add_qty, set_qty, **kw)

    @route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'],
                website=True)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: same as cart update if not customer are eligible then through error.
        """
        try:
            set_qty_int = set_qty and int(set_qty) or None
            add_qty_int = add_qty and int(add_qty) or None
        except Exception as e:
            set_qty_int = False
            add_qty_int = False
        if (set_qty_int and set_qty_int > 0) or (add_qty_int and add_qty_int > 0):
            current_user_partner = request.env.user and request.env.user.partner_id or False
            not_eligible_partner = request.website.elegible_customer(current_user_partner)
            if not_eligible_partner:
                request.session['not_elegible_customer_error'] = (
                    _("Your user is blocked, please contact the credit and collection area for "
                      "clarification."))
                return request.redirect('/shop')
        return super(SetuCustomerLock, self).cart_update_json(product_id, line_id,
                                                              add_qty=add_qty_int,
                                                              set_qty=set_qty_int, display=display,
                                                              **kw)

    @route(['/shop/cart/update_json/check_elegible'], type='json', auth="public",
                methods=['POST'], website=True)
    def cart_update_json_check_elegible(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: call from js and checked the condition if not eligible then through error .
        """
        try:
            set_qty_int = set_qty and int(set_qty) or False
            add_qty_int = add_qty and int(add_qty) or False
        except Exception as e:
            set_qty_int = False
            add_qty_int = False
        if (set_qty_int and set_qty_int > 0) or (add_qty_int and add_qty_int > 0):
            current_user_partner = request.env.user and request.env.user.partner_id or False
            not_eligible_partner = request.website.elegible_customer(current_user_partner)
            if not_eligible_partner:
                request.session['not_elegible_customer_error'] = (
                    _("Your user is blocked, please contact the credit and collection area for clarification."))
                return {'status': 'deny'}
        return {'success': 'allow'}
