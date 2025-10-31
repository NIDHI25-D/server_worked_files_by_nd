import pytz
from odoo.http import request, Controller, route
from datetime import datetime

from odoo import http, SUPERUSER_ID, _
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from odoo.addons.sale.controllers.portal import CustomerPortal

class WebsiteSalePreorder(WebsiteSale):

    def _get_search_options(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: add stock type during the select type.
        """
        options = super()._get_search_options(**post)
        options.update({
            'stock_type': post.get('stock_type'),
        })
        return options

    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: filtered the products and it's count.
        """
        fuzzy_search_term, product_count, search_result = super()._shop_lookup_products(attrib_set, options, post,
                                                                                        search, website)
        current_partner = request.env.user.partner_id.id
        search_result = search_result.filtered(lambda x:x.exclusive_partner_id.id in [current_partner,False])
        product_count = len(search_result)
        return fuzzy_search_term,product_count,search_result

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: added a stock type as per the select at the shop.
        """
        res = super().shop(page, category, search, ppg, **post)
        res.qcontext.update(**post)
        if not request.env.user._is_public():
            res.qcontext.get('keep').args.update({'stock_type': post.get('stock_type')})
        return res

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: called the method as it is if the Exclusive Partner are set in the product are match with the
            current partner or there are no Exclusive Partner else not opened and redirect to the shop.
        """
        current_partner = request.env.user.partner_id
        if product.exclusive_partner_id.id in [current_partner.id,False]:
            return super().product(product=product, category=category, search=search, **kwargs)
        else:
            return request.redirect('/shop')

    @http.route()
    def shop_payment_confirmation(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: if order is preorder or presale or international preorder than set a warehouse as per the set in a website
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order.is_preorder or order.is_presale or order.is_international_preorder:
                order.warehouse_id = order.website_id.warehouse_id
        res = super(WebsiteSalePreorder, self).shop_payment_confirmation(**post)
        return res

    @http.route()
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
            product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set a min quantity as per the product preorder_minimum_qty
        """
        product_min_qty = request.env['product.product'].browse(product_id).preorder_minimum_qty
        international_minimum_exclusivity_quantity = request.env['product.product'].browse(product_id).minimum_exclusivity_quantity
        if kw.get('is_exclusive') == 'True' and add_qty and add_qty < international_minimum_exclusivity_quantity:
            add_qty = int(international_minimum_exclusivity_quantity)
        if kw.get('is_exclusive') == 'True' and set_qty and set_qty < international_minimum_exclusivity_quantity:
            set_qty = int(international_minimum_exclusivity_quantity)
        if add_qty and add_qty < product_min_qty and not request.env['product.product'].browse(product_id).next_day_shipping:
            add_qty =int(product_min_qty)
        if set_qty and set_qty < product_min_qty and set_qty > 0 and not request.env['product.product'].browse(product_id).next_day_shipping:
            set_qty = int(product_min_qty)
        stock_type = kw.get('stock_type')
        order = request.website.sale_get_order()
        order.set_temp_stock_type(stock_type)

        # if stock_type:
        #     request.env.context = dict(request.env.context, stock_type=stock_type)


        return super(WebsiteSalePreorder, self).cart_update_json(product_id, line_id=line_id,add_qty=add_qty, set_qty=set_qty,
                                                                 display=display,
                                                                 product_custom_attribute_values= product_custom_attribute_values,
                                                                 no_variant_attribute_values= no_variant_attribute_values,
                                                                 **kw)

    @http.route()
    def shop_payment(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 15/04/25
            Task: Migration to v18 from v16
            Purpose: Remove non-presale products from a cart
        """
        order = request.website.sale_get_order()
        if order and order.is_presale:
            order.order_line.filtered(lambda x:not (x.product_id.available_for_presale or x.is_delivery)).unlink()
            if len(order.order_line) == 0:
                order.message_post(body=_("Products are now instock so we removed those products and cancel the sale order"))
                order.action_cancel()
        return super(WebsiteSalePreorder, self).shop_payment(**post)

    @http.route()
    def cart(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: called when clicked on cart and here checked if the order is internation type so perform operation as per the conditions.
        """
        order = request.website.sale_get_order()
        if order.is_international_preorder:
            for o_line in order.order_line.filtered(lambda x: not x.is_reward_line and not x.is_delivery):
                if o_line.product_id.is_international_pre_order_product and o_line.product_id.international_preorder_qty < o_line.product_id.minimum_exclusivity_quantity:
                    o_line.product_uom_qty = o_line.product_id.international_preorder_qty
                    if o_line.is_exclusive:
                        o_line.is_exclusive = False
                else:
                    if not o_line.product_id.is_international_pre_order_product:
                        o_line.unlink()
        return super().cart(**post)

class VariantControllerPreorder(WebsiteSaleVariantController):
    @route('/website_sale/get_combination_info', type='json', auth='public', methods=['POST'], website=True)
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, parent_combination=None, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the custom data to use it in template - preorderProductsInformation.
        """
        res = super().get_combination_info_website(
            product_template_id, product_id, combination, add_qty, parent_combination, **kwargs
        )
        product = request.env['product.product'].browse(res.get('product_id'))
        presale_incoming = preorder_incoming = international_preorder_incoming = []
        lang = request.env.context.get('lang')
        res.update({'lang': lang})
        website = request.env['website'].get_current_website()
        conf_warehouses = website._get_website_location_type()
        res.update({'free_qty': product.with_context(warehouse_id=conf_warehouses).free_qty})
        quantity_available = {'incoming_qty': 0, 'free_qty': res['free_qty'], 'presale_qty': 0,
                              'preorder_qty': 0, 'order_line': [], 'warehouse_dict': [],'calculated_qty': 0 ,'international_preorder_qty':0}
        stock_incoming = request.env['purchase.order.line'].with_user(SUPERUSER_ID).search_read(
            domain=[('product_id', 'in', product.ids), ('state', 'in', ['purchase']),
                    ('order_id.is_preorder_type', '=', False),
                    ('order_id.is_presale_type', '=', False),
                    ('order_id.is_international_pre_order', '=', False),
                    ('qty_received', '<', 1),
                    ('date_planned', '>', datetime.now().astimezone(pytz.timezone('America/Mexico_City')))],
            fields=['product_uom_qty', 'date_planned'], order="date_planned,id asc")
        if not conf_warehouses:
            warehouse_data = request.env['stock.warehouse'].with_user(SUPERUSER_ID).search_read(
                domain=[], fields=['name'],order="name")
        else:
            warehouse_data = request.env['stock.warehouse'].with_user(SUPERUSER_ID).search_read(
                domain=[('id', 'in', conf_warehouses)], fields=['name'], order="name")

        quantity_available['incoming_qty'] += sum([k['product_uom_qty'] for k in stock_incoming])
        quantity_available['order_line'].extend(
            [dict(item, **{'type': 'Stock', 'date_planned_mx': item['date_planned'].astimezone(
                pytz.timezone('America/Mexico_City')).date()}) for item in stock_incoming])
        quantity_available['warehouse_dict'].extend(
            dict(item, **{'name': item['name'], 'qty': product.with_context(warehouse_id=item['id']).free_qty}) for item in
            warehouse_data)
        quantity_available['warehouse_dict'] = [d for d in quantity_available.get('warehouse_dict') if d.get("qty") != 0]
        quantity_available['calculated_qty'] = product.calculated_qty
        if quantity_available.get('calculated_qty') == 0 :
            if res['free_qty'] >= website.minimum_amt_qty :
                quantity_available['calculated_qty'] = website.minimum_amt_qty
                factor = (quantity_available.get('calculated_qty') / res['free_qty']) * 100 if res.get('free_qty', 0) > 0 else 0
                quantity_available['warehouse_dict'] = [{**i, 'qty': round((i['qty'] * factor) / 100)} for i in
                                                        quantity_available.get('warehouse_dict')]
            if res['free_qty'] < website.minimum_amt_qty:
                quantity_available['calculated_qty'] = res['free_qty']
        else :
            if quantity_available.get('calculated_qty') >= res['free_qty']:
                quantity_available['calculated_qty'] = res['free_qty']
            else:
                #available quantities (426) are greater than the calculated quantities(400) so display 400
                factor = (quantity_available.get('calculated_qty') / res['free_qty']) * 100 if res.get('free_qty', 0) > 0 else 0
                quantity_available['warehouse_dict'] = [{**i, 'qty': round((i['qty'] * factor)/100)} for i in quantity_available.get('warehouse_dict')]
        if product.available_for_presale and website.enable_pre_sale and product.presale_price > 0:
            presale_incoming = request.env['purchase.order.line'].with_user(
                SUPERUSER_ID).search(
                domain=[('product_id', 'in', product.ids), ('state', 'in', ['purchase','done']),
                        ('order_id.is_presale_type', '!=', False), ('qty_received', '<', 1), ('product_qty', '>=', 1),
                        ('date_planned', '>', datetime.now().astimezone(pytz.timezone('America/Mexico_City')))],
                order="date_planned asc").filtered(lambda x: x.product_qty != x.pre_sale_qty)
            if presale_incoming:
                presale_incoming = presale_incoming[0].read(
                    fields=['pre_sale_qty', 'product_uom_qty', 'date_planned'])
            quantity_available['incoming_qty'] += sum(
                [k['product_uom_qty'] for k in presale_incoming])
            quantity_available['presale_qty'] += sum(
                [k['product_uom_qty'] - k['pre_sale_qty'] for k in presale_incoming])
            quantity_available['order_line'].extend(
                [dict(item, **{'type': '%s' % _('Presale'),
                               'date_planned_mx': item['date_planned'].astimezone(
                                   pytz.timezone('America/Mexico_City')).date()}) for item in
                 presale_incoming])
        if product.available_for_preorder and website.enable_pre_order:
            preorder_incoming = request.env['purchase.order.line'].with_user(
                SUPERUSER_ID).search_read(
                domain=[('product_id', 'in', product.ids), ('state', 'in', ['draft']),
                        ('order_id.is_preorder_type', '!=', False),
                        ('date_planned', '>', datetime.now().astimezone(pytz.timezone('America/Mexico_City')))],
                fields=['pre_ordered_qty', 'product_uom_qty', 'date_planned'],
                order="date_planned,id asc")
            quantity_available['incoming_qty'] += sum(
                [k['product_uom_qty'] for k in preorder_incoming])
            quantity_available['preorder_qty'] += sum(
                [k['product_uom_qty'] - k['pre_ordered_qty'] for k in preorder_incoming])
            quantity_available['order_line'].extend(
                [dict(item,
                      **{'type': '%s' % _('Preorder'), 'date_planned_mx': item['date_planned'].astimezone(
                          pytz.timezone('America/Mexico_City')).date()}) for item in
                 preorder_incoming])

        if product.is_international_pre_order_product:
            international_preorder_incoming = request.env['purchase.order.line'].with_user(SUPERUSER_ID).search_read(
                domain=[('product_id', 'in', product.ids), ('state', 'in', ['draft']),
                        ('order_id.is_international_pre_order', '!=', False),
                        ('date_planned', '>', datetime.now().astimezone(pytz.timezone('America/Mexico_City')))],
                fields=['international_pre_order_qty', 'product_uom_qty', 'date_planned'],
                order="date_planned,id asc")
            quantity_available['incoming_qty'] += sum(
                [k['product_uom_qty'] for k in international_preorder_incoming])
            quantity_available['international_preorder_qty'] += sum(
                [k['product_uom_qty'] - k['international_pre_order_qty'] for k in international_preorder_incoming])

        res.update({
            'is_preorder': product.available_for_preorder,
            'preorder_qty': product.preorder_qty,
            # 'preorder_qty': quantity_available.get('preorder_qty'),
            'preorder_free_qty': product.preorder_qty - sum(
                [k['pre_ordered_qty'] for k in preorder_incoming]),
            'preorder_incoming': preorder_incoming,
            'is_presale': product.available_for_presale,
            'presale_qty': product.presale_qty,
            # 'presale_qty': quantity_available.get('presale_qty'),
            'presale_free_qty': product.presale_qty - sum(
                [k['pre_sale_qty'] for k in presale_incoming]),
            'presale_incoming': presale_incoming,
            'is_next_day_shipping': product.next_day_shipping,
            'default_code': product.default_code,
            'quantity_available': quantity_available,
            'minimum_qty_for_preorder_presale': product.preorder_minimum_qty,
            'presale_price':product.presale_price_incl_tax,
            # 'presale_price': product.presale_price,
            'is_international_pre_order_product': product.is_international_pre_order_product,
            'international_preorder_qty':product.international_preorder_qty,
            'international_preorder_free_qty': product.international_preorder_qty - sum(
                [k['international_pre_order_qty'] for k in international_preorder_incoming]),
            'international_preorder_incoming' : international_preorder_incoming,
            'minimum_exclusivity_quantity': product.minimum_exclusivity_quantity,
            'delivery_estimated_time':product.delivery_estimated_time,
            'intl_preorder_msg':website.international_preorder_msg,
            'website_presale_msg': website.presale_msg,
        })
        order = request.website.sale_get_order()

        if order.is_preorder:
            res['order_type'] = 'preorder'
            if res.get('lang') == 'en_US':
                res['msg'] = 'You can not add this product as your cart contains preorder type products'
            else:
                res['msg'] = 'No puede agregar este producto ya que su carrito contiene productos de tipo Pre-Orden'
        elif order.is_presale:
            res['order_type'] = 'presale'
            if res.get('lang') == 'en_US':
                res['msg'] = 'You can not add this product as your cart contains presale type products'
            else:
                res['msg'] = 'No puede agregar este producto ya que su carrito contiene productos de tipo Pre-Venta'
        elif order.is_next_day_shipping:
            res['order_type'] = 'is_next_day_shipping'
            if res.get('lang') == 'en_US':
                res['msg'] = 'You can not add this product as your cart contains next day shipping type products'
            else:
                res['msg'] = 'No puede agregar este producto ya que su carrito contiene productos de envío al día siguiente.'
        elif order.is_international_preorder:
            res['order_type'] = 'international_preorder'
            if res.get('lang') == 'en_US':
                res['msg'] = 'You can not add this product as your cart contains international preorder type products'
            else:
                res['msg'] = 'No puede agregar este producto ya que su carrito contiene productos de tipo Pre-Orden Internacional'
        elif not (order.is_preorder and order.is_presale and order.is_international_preorder and order.is_next_day_shipping) and order.order_line:
            res['order_type'] = 'stock'
            if res.get('lang') == 'en_US':
                res['msg'] = 'You can not add this product as your cart contains stock type products'
            else:
                res['msg'] = 'No puede agregar este producto ya que su carrito contiene productos de tipo Stock'
        else:
            res['order_type'] = ''
        return res

class SetuCancelOrder(CustomerPortal):
    def portal_order_page(self, order_id=None, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16 --> Website - enhancement { https://app.clickup.com/t/86dtwa8bt }
            Purpose: This controller is to pass the current_date and cancel_order_time_limit_controller to the XML(template=inherit_sale_order_re_order_btn_for_order_again).
        """
        response = super(SetuCancelOrder, self).portal_order_page(order_id=order_id, **post)
        if response.qcontext.get('sale_order') and response.qcontext.get('sale_order').state in ('sale','done'):
            sale_order_rec = response.qcontext.get('sale_order')
            if sale_order_rec.cancel_order_time_limit:
                response.qcontext.update({
                    'current_date_sale_order': datetime.now().astimezone(pytz.timezone(request.env.user.tz)),
                    'cancel_order_time_limit_controller':sale_order_rec.cancel_order_time_limit.astimezone(pytz.timezone(request.env.user.tz))
                })
        return response

class CancelOrderBySetu(http.Controller):
    @http.route(['/shop/cancel_order'], type='json', auth="public", website=True)
    def cancel_order_enhacement(self,order_id):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16 --> Website - enhancement { https://app.clickup.com/t/86dtwa8bt }
            Purpose: This url is called from website_sale_cancel.js.
                     This method is called when the user wants to cancel the order from the website whith the time limit mentioned in the Settings.
                     It will enable the boolean: Order canceled from Website of the Sale order when the Order is canceled from Website.
                     It will cancel both Sale order and Picking/s (only if Assortments dates are not mentioned in the picking, this is handled from XML side).
        """
        sale_order = request.env['sale.order'].sudo().browse(order_id)
        if datetime.now().astimezone(pytz.timezone(request.env.user.tz)) <= sale_order.cancel_order_time_limit.astimezone(pytz.timezone(request.env.user.tz)):
            if not sale_order.picking_ids.filtered(lambda x: x.assortment_start_date):
                sale_order_cancel = sale_order.with_context(disable_cancel_warning=True).action_cancel()
                sale_order.sale_order_cancel_from_website = True
                website = request.env['website'].get_current_website()
                for picking in sale_order.picking_ids:
                    picking.order_fill_error_picking_id = website.cancellation_reason_for_picking_id
                picking_cancel = sale_order.picking_ids.action_cancel()
                _logger.info("Sale order cancel from website: %s ",sale_order.name)
                return {'sale_order_cancel': sale_order_cancel, 'picking_cancel':picking_cancel}
        elif datetime.now().astimezone(pytz.timezone(request.env.user.tz)) > sale_order.cancel_order_time_limit.astimezone(pytz.timezone(request.env.user.tz)):
            raise UserError(_("Sorry, you can't cancel this order"))
        return sale_order