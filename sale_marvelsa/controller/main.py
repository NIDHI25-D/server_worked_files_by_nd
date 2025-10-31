# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, _, SUPERUSER_ID
from odoo.http import request,route
import logging
import datetime
from odoo.addons.website_sale.controllers.delivery import Delivery

_logger = logging.getLogger("credit_of_pricelist")


class WebsiteSaleExt(WebsiteSale):

    @http.route()
    def shop_payment_confirmation(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/01/25
            Task: Migration to v18 from v16
            Purpose: confirm a sale order as per the order pricelist and partner_id
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            order_type = False
            if not order.is_terms_and_condition_accepted:
                order.is_terms_and_condition_accepted = True
                order.terms_and_condition_date = datetime.date.today()
                order.message_post(body=_("The terms and conditions for the order %s are accepted on %s") % (
                            order.name, datetime.date.today()))
            if hasattr(order,'is_preorder') or hasattr(order,'is_presale'):
                order_type = order.is_preorder or order.is_presale
            if order and not order_type and order.state not in ('sale', 'done') and order.pricelist_id.is_credit and order.partner_id.credit_limit and (
                    order.amount_total + order.partner_id.total_due) < order.partner_id.credit_limit and order.partner_id.total_overdue <= 0:
                order.with_user(SUPERUSER_ID).action_confirm()
            if not order.pricelist_id.is_credit:
                _logger.info(f"Price list {order.pricelist_id.name}({order.pricelist_id.id}) has credit False")
            if order.pricelist_id.payment_term_for_priceslist_id:
                order.payment_term_id = order.pricelist_id.payment_term_for_priceslist_id
            else:
                if order.partner_id.property_payment_term_id:
                    order.payment_term_id = order.partner_id.property_payment_term_id
            order and order.get_payment_way()
        res = super(WebsiteSaleExt, self).shop_payment_confirmation(**post)
        return res


    @http.route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/01/25
            Task: Migration to v18 from v16
            Purpose: to set a payment_term_id and other values when validate.
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order and order.pricelist_id.payment_term_for_priceslist_id:
                order.payment_term_id = order.pricelist_id.payment_term_for_priceslist_id
        res = super().shop_payment_validate(sale_order_id, **post)
        order = request.website.sale_get_order()
        tx = order.get_portal_last_transaction() if order else order.env['payment.transaction']
        if order:
            if order and not order.amount_total and not tx:
                request.session['sale_last_order_id'] = False
                request.session['sale_order_id'] = False
                request.session['website_sale_cart_quantity'] = 0
        return res


class WebsiteSaleMarvel(Delivery):

    @http.route()
    def shop_set_delivery_method(self, dm_id, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 24/01/25
            Task: Migration to v18 from v16
            Purpose: to set a display_msg_on_web field from carrier for displaying it in website.
        """
        res = super().shop_set_delivery_method(dm_id, **kwargs)
        carrier = request.env['delivery.carrier'].sudo().browse(int(dm_id))
        display_msg_on_web = carrier.display_message_on_website
        res.update({'display_msg_on_web': display_msg_on_web if display_msg_on_web else ''})
        return res

    @route('/shop/get_delivery_rate', type='json', auth='public', methods=['POST'], website=True)
    def shop_get_delivery_rate(self, dm_id):
        """
            Author: nidhi@setconsulting.com
            Date: 27/08/25
            Task: Error displaying message on website { https://app.clickup.com/t/86dx4mc06}
            Purpose: display_msg_on_web on all carrier if message set on carrier
        """
        res = super().shop_get_delivery_rate(dm_id)
        carrier = request.env['delivery.carrier'].sudo().browse(int(dm_id))
        display_msg_on_web = carrier.display_message_on_website
        res.update({'display_msg_on_web': display_msg_on_web if display_msg_on_web else ''})
        return res
