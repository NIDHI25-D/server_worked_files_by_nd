from odoo import http, _
from odoo.http import request
from .RestHelper import RestHelper
from typing import Dict
import json
from ..models.ratelimiter import RateLimiter
import re
from datetime import datetime
from werkzeug.exceptions import HTTPException
import logging
_logger = logging.getLogger(__name__)

class RateLimitExceeded(HTTPException):
    def get_response(self, environ=None):
        """
            Author: nidhi@setconsulting.com
            Date: 19/07/24
            Task: Rest API phase 2
            Purpose: This method is used give to error: Ratelimit exceeded once the limit mentioned in the Setting is complete.
                     It will also set status_code to 429 in Postman and also seen in log.
        """
        response = super().get_response(environ)
        response.data = json.dumps({'error': 'Ratelimit exceeded'})
        response.content_type = 'application/json'
        response.status_code= 429
        return response

ENDPOINT = '/api'


class RestController(http.Controller):

    @http.route([f'{ENDPOINT}/get_customer_information',f'{ENDPOINT}/get_pricelist'], auth="user", type="json", methods=['POST'], csrf=False)
    def get_customer_information(self) -> Dict[str, any]:
        """
            Author: kishan@setuconsulting
            Date: 13/02/24
            Task: Rest api
            Purpose: To get customer information
        """


        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id',False)
        if not partner_id or type(partner_id) != int:
            return {
                'error': True,
                'message': 'Please enter valid json data'
            }
        try:
            if partner_id:
                data = self.check_partner_info(partner_id)
                if data.get('error'):
                    return data
                record = request.env['res.partner'].sudo().search(
                    [('id', '=', int(partner_id)), ('active', '=', True)])
                if not record:
                    return {
                        'error': True,
                        'message': 'partner_id is not there in the system'
                    }
                if request.httprequest.base_url.split('/')[-1] == 'get_customer_information':
                    delivery_partner_ids = False
                    fields = ['name']
                    if record.child_ids:
                        delivery_partner_ids = record.child_ids.filtered(lambda type:type.type == 'delivery')
                    record = record.read(fields)
                    if delivery_partner_ids:
                        record[0].update({'delivery_partner_ids':delivery_partner_ids.read(['name'])})
                    customer_data = {'customer_data':record}
                if request.httprequest.base_url.split('/')[-1] == 'get_pricelist':
                    allowed_pricelist_ids = record.allowed_pricelists.filtered(lambda x: x.selectable).read(
                        ['id', 'name']) if record.allowed_pricelists and record.allowed_pricelists.filtered(
                        lambda x: x.selectable) else []
                    extra_pricelistt_ids = record.extra_pricelist.filtered(lambda x: x.selectable).read(
                        ['id', 'name']) if record.extra_pricelist and record.extra_pricelist.filtered(
                        lambda x: x.selectable) else []
                    customer_data = {'pricelists':allowed_pricelist_ids + extra_pricelistt_ids}
                    fields = ['allowed_pricelists','extra_pricelist']
                return customer_data
        except Exception as e:
            return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))

    @http.route([f'{ENDPOINT}/get_available_stock'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_product_information(self) -> Dict[str, any]:
        """
            Author: kishan@setuconsulting
            Date: 19/02/24
            Task: Rest api
            Purpose: To get available stock of products
        """

        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        product_ids = converted_data.get('product_ids', [])
        if not product_ids or not set(map(type, product_ids)) == {str}:
            return {
                'error': True,
                'message': 'Please enter valid json data or you must add some products to request the product stock.'
            }
        # TASK: Rest API phase 2
        api_name = 'api_get_available_stock'
        config = request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.api_get_available_stock')
        if config:
            minutes_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_available_stock'))
            limit_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_available_stock'))
            _logger.info(f"Minutes for API- {api_name}: {minutes_for_api}, Limit for API- {api_name}: {limit_for_api}")
            rate_limiter = RateLimiter.get_rate_limiter(api_name, request.env)
            user_id = request.env['ir.http'].session_info().get('uid', 0)
            key = user_id
            if rate_limiter.is_rate_limited(key, api_name, request.env):
                raise RateLimitExceeded()
            remaining = rate_limiter.remaining_requests(key, api_name, request.env)
            _logger.info(f"Remaining requests for api {api_name}: {remaining}")
             #0th will be count for 0th time

        try:
            if product_ids:
                website = request.env['website'].get_current_website()
                stock_pick_type = website.stock_pick_type

                location_ids = []
                if stock_pick_type == 'Specific':
                    location_ids = request.env['stock.location'].search([('warehouse_id', '=', website.warehouse_default_id.id), ('usage', '=', 'internal')]).ids
                elif stock_pick_type == 'Several':
                    location_ids = request.env['stock.location'].search([('warehouse_id', 'in', website.warehouse_default_ids.ids), ('usage', '=', 'internal')]).ids
                else:
                    location_ids = request.env['stock.location'].search([('usage', '=', 'internal')]).ids

                query = """
                    SELECT
                        pp.id as product_id,
                        pp.default_code as internal_reference,
                        pt.name as product_name,
                        SUM(sq.quantity - sq.reserved_quantity) as quantity
                    FROM
                        product_product pp
                    LEFT JOIN
                        product_template pt ON pt.id = pp.product_tmpl_id
                    LEFT JOIN
                        stock_quant sq ON sq.product_id = pp.id AND sq.location_id = ANY(%s)
                    WHERE
                        pp.default_code IN %s AND pp.active = TRUE
                    GROUP BY
                        pp.id, pt.name
                """

                params = (location_ids, tuple(product_ids))
                request.cr.execute(query, params)
                data = request.cr.dictfetchall()
                product_dictionary = []
                if not data:
                    return {
                        'error': True,
                        'message': f"There is not relevant data"
                    }

                for product in data:
                    quantity = product.get('quantity') or 0
                    if quantity > 0:
                        product_dictionary.append({
                            "internal_reference": product.get('internal_reference'),
                            "product_name": product.get('product_name'),
                            "available_qty": quantity
                        })

                return {"products": product_dictionary}
        except (KeyError, FileNotFoundError) as e:
            _logger.error(f"Filestore or cache error: {e}")
            return RestHelper.JsonErrorResponse(_(f"Internal server error: Filestore or cache issue."))
        except Exception as e:
            return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))

    @http.route([f'{ENDPOINT}/get_payment_methods'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_payment_methods(self) -> Dict[str, any]:
        """
            Author: kishan@setuconsulting
            Date: 26/02/24
            Task: Rest api
            Purpose: To get payment method as per configuration
        """

        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', [])
        if not partner_id or type(partner_id) != int:
            return {
                'error': True,
                'message': 'Please enter valid json data '
            }
        try:
            data = self.check_partner_info(partner_id)
            if data.get('error'):
                return data
            payment_ids = eval(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.payment_method_ids'))
            # payment_ids = request.env['ir.default'].sudo().get('res.config.settings', 'payment_method_ids', company_id=request.env.company.id)
            if not payment_ids:
                return {
                    'error': True,
                    'message': 'There are not any configure payments.'
                }
            payment_ids = request.env['l10n_mx_edi.payment.method'].sudo().browse(payment_ids)
            payment_ids = payment_ids.read(['name'])
            return {"Payment Ways": payment_ids}
        except Exception as e:
            return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))

    @http.route([f'{ENDPOINT}/get_product_prices'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_product_prices(self) -> Dict[str, any]:
        """
            Author: kishan@setuconsulting
            Date: 05/03/24
            Task: Rest api
            Purpose: To get product pricelist information
        """
        # TASK : Rest API phase 2
        api_name = 'api_get_product_prices'
        config = request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.api_get_product_prices')
        if config:
            minutes_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_product_prices'))
            limit_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_product_prices'))
            _logger.info(f"Minutes for API- {api_name}: {minutes_for_api}, Limit for API- {api_name}: {limit_for_api}")
            rate_limiter = RateLimiter.get_rate_limiter(api_name, request.env)
            user_id = request.env['ir.http'].session_info().get('uid', 0)
            key = str(user_id)
            if rate_limiter.is_rate_limited(key, api_name, request.env):
                raise RateLimitExceeded()
            remaining = rate_limiter.remaining_requests(key, api_name, request.env)
            _logger.info(f"Remaining requests for api {api_name}: {remaining}")
            # 0th will be count for 0th time

        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', False)
        pricelist_id = converted_data.get('pricelist_id', False)
        product_ids = converted_data.get('product_ids', False)

        if not product_ids or not set(map(type, product_ids)) == {str}:
            return {
                'error': True,
                'message': 'Please enter valid json data or you must add some products to request the product stock.'
            }
        if not all([partner_id,pricelist_id]) or not set(map(type, [partner_id,pricelist_id])) == {int}:
            return {
                'error': True,
                'message': 'Please enter proper partner_id or pricelist_id.'
            }
        partner_obj = request.env['res.partner'].sudo().search(
            [('id', '=', int(partner_id)), ('active', '=', True)])

        pricelist_obj = request.env['product.pricelist'].sudo().search(
            [('id', '=', int(pricelist_id)), ('active', '=', True)])

        if not all([partner_obj,pricelist_obj]):
            message = []
            if not partner_obj:
                message.append(f"Contact with {partner_id} not found in system")
            if not pricelist_obj:
                message.append(f"Pricelist  is not related to your requesting user")
            if message:
                return {
                    'error': True,
                    'message': message
                }


        data = self.check_partner_info(partner_id)
        if data.get('error'):
            return data

        if partner_obj and pricelist_obj and (partner_obj.allowed_pricelists or partner_obj.extra_pricelist):
            message = []
            if pricelist_obj.id not in (
                    (partner_obj.allowed_pricelists.ids if partner_obj.allowed_pricelists else []) + (
                    partner_obj.extra_pricelist.ids if partner_obj.extra_pricelist else [])):
                message.append(f"Pricelist with {pricelist_obj.id} not in your allowed pricelist.")
                return {
                    'error': True,
                    'message': message
                }
        product_information = []
        products_ids = request.env['product.product'].sudo().search([('default_code','in',product_ids)])
        for product_id in products_ids:
            price = pricelist_obj._get_products_price(product_id,1)
            price = round(price[product_id.id],2)

            taxes = product_id.taxes_id
            lst_price = product_id.lst_price
            discount = round(lst_price - price, 2)

            taxes_res = taxes.compute_all(
                price,
                product=product_id,
                partner=False,
            )
            amount = 0.0
            included,excluded = taxes_res.get('total_included'),taxes_res.get('total_excluded')
            for tax in taxes_res.get('taxes'):
                amount += tax.get('amount',0)
            product_information.append({
                'product_name':product_id.name,
                'internal_reference':product_id.default_code,
                "sales_price": round(lst_price,2),
                "sales_price_after_pricelist":round(price,2),
                "tax_amount":round(amount,2),
                "final_price": included
            })
        return {"Products":product_information}




    @http.route([f'{ENDPOINT}/create_sale_order'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def create_sale_order(self) -> Dict[str, any]:
        """
            Author: kishan@setuconsulting
            Date: 05/03/24
            Task: Rest api
            Purpose: To create sale orders
        """
        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', False)
        price_list_id = converted_data.get('price_list_id', False)
        items = converted_data.get('items', [])
        delivery_address_id = converted_data.get('delivery_address_id', False)
        payment_method_id = converted_data.get('payment_method', False)
        check_result = self.check_sale_order_data(converted_data,partner_id,price_list_id,items,delivery_address_id,payment_method_id)
        if check_result['error'] == False:
            data = self.final_create_order(converted_data,partner_id,price_list_id,items,delivery_address_id,payment_method_id)
            return {
                'error': False,
                'Sale order information': data
            }
        else:
            return check_result

    def check_sale_order_data(self,converted_data,partner_id,price_list_id,items,delivery_address_id,payment_method_id):
        """
            Author: kishan@setuconsulting
            Date: 05/03/24
            Task: Rest api
            Purpose: To check valid data to create sale order
        """
        check_result = {}


        if len(converted_data) == 0:
            check_result.update({
                'error': True,
                'message': 'JSON request is empty'
            })
            return check_result

        if not all([partner_id,price_list_id,items,payment_method_id]) or not set(map(type, [price_list_id,payment_method_id] + ([delivery_address_id] if delivery_address_id else []))) == {int}:
            check_result.update({
                'error': True,
                'message': 'Please add proper json request data to create sale order'
            })
            return check_result

        for item in items:
            internal_reference = item.get('internal_reference')
            quantity = item.get('quantity')
            product_obj = request.env['product.product']
            if not internal_reference or not quantity or type(internal_reference) != str or type(quantity) != int:
                check_result.update({
                    'error': True,
                    'message': 'Please add proper Internal reference or quantity'
                })
                return check_result
            product_id = product_obj.sudo().search(
                [('default_code', '=', internal_reference),('active','=',True)], limit=1)
            if not product_id:
                check_result.update({
                    'error': True,
                    'message': f"Product {internal_reference} not found in system"
                })
                return check_result

        partner_obj = request.env['res.partner'].sudo().search(
            [('id', '=', int(partner_id)), ('active', '=', True)])

        pricelist_obj = request.env['product.pricelist'].sudo().search(
            [('id', '=', int(price_list_id)), ('active', '=', True)])
        payment_obj = request.env['l10n_mx_edi.payment.method'].sudo().search(
            [('id', '=', int(payment_method_id)), ('active', '=', True)])

        if not all([partner_obj,pricelist_obj,payment_obj]):
            message = []
            if not partner_obj:
                message.append(f"Contact with {payment_method_id} not found in system")
            if not pricelist_obj:
                message.append(f"Pricelist with {price_list_id} not found in system")
            if not payment_obj:
                message.append(f"Payment with {payment_method_id} not found in system")
            if message:
                check_result.update({
                    'error': True,
                    'message': message
                })
                return check_result

        data = self.check_partner_info(partner_id)
        if data.get('error'):
            return data
        
        if partner_obj and pricelist_obj:
            message = []
            delivery_address_obj = False
            delivery_partner_ids = []
            if partner_obj.allowed_pricelists or partner_obj.extra_pricelist:
                if pricelist_obj.id not in ((partner_obj.allowed_pricelists.ids if partner_obj.allowed_pricelists else []) + (partner_obj.extra_pricelist.ids if partner_obj.extra_pricelist else [])):
                    message.append(f"{pricelist_obj.id} not in allowed pricelist.")
            if message:
                check_result.update({
                    'error': True,
                    'message': message
                })
                return check_result
            if delivery_address_id and int(delivery_address_id) != partner_obj.id:
                delivery_address_obj = request.env['res.partner'].sudo().search(
                    [('id', '=', int(delivery_address_id)), ('active', '=', True)])
                if not delivery_address_obj:
                    message.append(f"Delivery partner you have added not in systyem.")
                    check_result.update({
                        'error': True,
                        'message': message
                    })
                    return check_result
                if partner_obj.child_ids:
                    delivery_partner_ids = partner_obj.child_ids.filtered(lambda type: type.type == 'delivery')
                if (delivery_address_obj and not delivery_partner_ids) or (delivery_address_obj and delivery_partner_ids and (delivery_address_obj.id not in delivery_partner_ids.ids)):
                    message.append(f"Delivery Partner is not correct in json request")
                if message:
                    check_result.update({
                        'error': True,
                        'message': message
                    })
                    return check_result

            payment_ids = eval(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.payment_method_ids'))

            if payment_obj and payment_obj.id not in payment_ids:
                check_result.update({
                    'error': True,
                    'message': f"Payment method is not in configuration."
                })
                return check_result





        check_result.update({
            'error': False
        })

        return check_result

    def final_create_order(self,converted_data,partner_id,price_list_id,items,delivery_address_id,payment_method_id):

        vals = {
            "partner_id": int(partner_id),
            "pricelist_id": int(price_list_id),
            "l10n_mx_edi_payment_method_id":int(payment_method_id)
        }

        if delivery_address_id:
            delivery_address_obj = request.env['res.partner'].sudo().search(
                [('id', '=', int(delivery_address_id)), ('active', '=', True)])
            vals.update({'partner_shipping_id':delivery_address_obj.id if delivery_address_obj else  int(partner_id)})
        order_line_list = []

        for item in items:
            internal_reference = item.get('internal_reference')
            quantity = item.get('quantity')
            product_obj = request.env['product.product']
            product_id = product_obj.sudo().search(
                [('default_code', '=', internal_reference),('active','=',True)], limit=1)
            order_line_list.append((0,0,{"product_id":product_id.id,"product_uom_qty":quantity}))
        vals.update({"order_line":order_line_list})

        sale_order_id = request.env['sale.order'].sudo().create(vals)
        # It will apply directly discount in the sale orders
        sale_order_id._update_programs_and_rewards()
        sale_order_id._auto_apply_rewards()

        sale_order_id._compute_warehouse_id()
        sale_order_id.l10n_mx_edi_payment_method_id = int(payment_method_id)
        quotation_send_obj = sale_order_id.action_quotation_send()
        email_ctx = quotation_send_obj.get('context', {})
        sale_order_id.with_context(**email_ctx).message_post_with_source(
            request.env['mail.template'].browse(email_ctx.get('default_template_id')), subtype_xmlid='mail.mt_comment',
        )
        sale_order_id.state = 'sent'
        sale_order_id.api_create_sale_order = True
        sale_order_id.customer_confirmation_date = datetime.now()
        data = {
            "Name": sale_order_id.name,
            "status": "Quotation Sent",
            "customer_name": sale_order_id.partner_id.name,
            "delivery_address_id": sale_order_id.partner_shipping_id.id,
            "delivery_Address": sale_order_id.partner_shipping_id.name,
            "price_list": sale_order_id.pricelist_id.name,
            "subtotal": sale_order_id.amount_untaxed,
            "taxes_amount": sale_order_id.amount_tax,
            "total": sale_order_id.amount_total,
            "api_create_sale_order":True,
            "customer_confirmation_date": datetime.now()
        }
        product_info = []
        for line in sale_order_id.order_line:
            product_id = line.product_id
            total_price = round(line.price_unit,2)
            tax_amount = round(line.price_tax,2)

            product_info.append({
                "internal_reference": product_id.default_code,
                'product_name':product_id.name,
                "ordered_qty": line.product_uom_qty,
                "UOM": line.product_uom.name,
                "unit_price": line.price_unit,
                "total": total_price,
                "Tax":line.tax_id.mapped('name'),
                "tax_amount":tax_amount,
                "untaxed_amount": total_price - tax_amount

            })
            data.update({
                "products":product_info
            })
        return data

    def check_partner_info(self,partner_id):
        uid_info = request.env['ir.http'].session_info().get('uid', 0)
        if not uid_info:
            return {
                'error': True,
                'message': 'User with you want to get information is not active or something went wrong'
            }
        user_id = request.env['res.users'].sudo().search([('id', '=', uid_info), ('active', '=', True)])
        if not user_id or user_id.partner_id.id != int(partner_id):
            return {
                'error': True,
                'message': 'partner_id is not related to your requesting user'
            }
        return {'error':False}

    @http.route([f'{ENDPOINT}/get_product_list'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_product_list(self) -> Dict[str, any]:
        """
            Author: jay@setuconsulting
            Date: 5/06/24
            Task: Rest API phase 2 { https://app.clickup.com/t/86dt666wc :comment --> https://app.clickup.com/t/86dt666wc?comment=90170028294265}
            Purpose: To get payment category as per configuration (setting with parameter partner_id)
            modified : add this part "Total Products":len(prod_prod_sku) task--> Get product list { https://app.clickup.com/t/86dx1dcuc?comment=90170141966074 }
        """
        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', [])

        # LOG 1: Validar el partner_id recibido
        _logger.info(f"API call received for partner_id: {partner_id}")

        if not partner_id or type(partner_id) != int:
            return {
                'error': True,
                'message': 'Please enter valid json data '
            }
        try:
            data = self.check_partner_info(partner_id)
            if data.get('error'):
                return data
            
            prod_category_id = request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.product_category_id')

            # LOG 2: Validar el ID de la categoría configurado en el sistema
            _logger.info(f"Configured product category ID: {prod_category_id}")

            if not prod_category_id:
                return {
                    'error': True,
                    'message': 'There are not any configure Product Category.'
                }

            # Paso 1: Encuentra la categoría padre y todas sus hijas.
            prod_cat_id = request.env['product.category'].sudo().browse(int(prod_category_id))
            all_category_ids = request.env['product.category'].sudo().search([('id', 'child_of', prod_cat_id.id)]).ids

            # LOG 3: Validar la lista completa de IDs de categorías a buscar
            _logger.info(f"Searching in category IDs: {all_category_ids}")

            # Paso 2: Usa la lista completa de IDs para buscar los productos.
            prod_prod_sku = request.env['product.product'].sudo().search([
                ('categ_id', 'in', all_category_ids),
                ('sale_ok', '=', True),
                ('product_tmpl_id.is_published', '=', True)
            ], limit=None).mapped('default_code')

            # LOG 4: Validar el resultado final de la búsqueda antes de devolverlo
            _logger.info(f"Found products with SKUs: {prod_prod_sku}")

            return {"Product List": prod_prod_sku, "Total Products":len(prod_prod_sku)}
        except Exception as e:
            # LOG 5: Capturar cualquier error inesperado
            _logger.error(f"An unexpected error occurred: {e}")
            return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))

    @http.route([f'{ENDPOINT}/get_sku_details'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_sku_details(self) -> Dict[str, any]:
        """
            Author: jay@setuconsulting
            Date: 5/06/24
            Task: Rest API phase 2 { https://app.clickup.com/t/86dt666wc : comment --> https://app.clickup.com/t/86dt666wc?comment=90170028294265}
            Purpose: To get payment category's details as per configuration (setting with parameter partner_id and sku)
        """
        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', [])
        product_ids = converted_data.get('default_code', [])
        pattern = re.compile('<[^>]*>')
        if not product_ids or not set(map(type, product_ids)) == {str}:
            return {
                'error': True,
                'message': 'Please enter valid json data or you must add some products to request the product stock.'
            }
        try:
            if product_ids :
                product_dictionary = []
                data = self.check_partner_info(partner_id)
                if data.get('error'):
                    return data
                prod_category_id = eval(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.product_category_id'))
                if not prod_category_id:
                    return {
                        'error': True,
                        'message': 'There are not any configure Product Category.'
                    }
                prod_cat_id = request.env['product.category'].sudo().browse(prod_category_id)
                prod_prod_sku = request.env['product.product'].sudo().search(
                    [('categ_id', 'child_of', prod_cat_id.ids), ('sale_ok', '=', True)])
                matching_codes = [code for code in product_ids if code in prod_prod_sku.mapped('default_code')]
                if matching_codes:
                    matching_records = [record for record in prod_prod_sku if record.default_code in matching_codes]
                    for product_prod in matching_records:
                        attri_list = []
                        unspsc_code = []
                        if product_prod.attribute_line_ids:
                            for attribute in product_prod.attribute_line_ids:
                                val_list = []
                                val_list2 = []
                                for value in attribute.value_ids:
                                    val_list2.append(value.name)
                                val_list.append({"value_name": val_list2})
                                attri_list.append({"name": attribute.attribute_id.name,
                                                   "values": val_list})
                        unspsc_code.append({
                            "code": product_prod.unspsc_code_id.code,
                            "name": product_prod.unspsc_code_id.name
                        }),
                        
                        def get_category_path(category):
                            path = []
                            current = category
                            while current:
                                # Si la categoría actual no tiene un padre, es la raíz.
                                # No la añadimos a la ruta.
                                if current.parent_id:
                                    path.insert(0, current.name)
                                current = current.parent_id
                            return ' / '.join(path)

                        product_dictionary.append({
                                                "name": product_prod.name,
                                                "internal_reference": product_prod.default_code,
                                                "list_price": round(product_prod.list_price,2),
                                                "brand":product_prod.product_brand_id.name,
                                                "taxes":product_prod.taxes_id.mapped('name'),
                                                "product_category_id": product_prod.categ_id.id, # <--- ¡SE AÑADIÓ ESTA LÍNEA!
                                                "product_category": get_category_path(product_prod.categ_id),
                                                "barcode": product_prod.barcode,
                                                "marca_ids": product_prod.marca_ids.mapped('name'),
                                                "uom_id":product_prod.uom_id.name,
                                                "compatible_ids":product_prod.compatible_ids.mapped('name'),
                                                "website_description":re.sub('amp;', ' ', re.sub('&nbsp;', ' ', re.sub(pattern, ' ', product_prod.descriptive_website_products))) if product_prod.descriptive_website_products else False,
                                                "unspsc_code_id": unspsc_code,
                                                "atrributes": attri_list if attri_list else [],
                                                "accessory_product_ids":product_prod.accessory_product_ids.mapped('default_code'),
                                                "alternative_product_ids":product_prod.alternative_product_ids.mapped('default_code'),
                                                "spare_parts_product_ids":product_prod.spare_parts_product_ids.mapped('default_code')
                        })
                    return {"Products":product_dictionary }
                else:
                    return {
                        'error': True,
                        'message': f"There is not relevant data"
                    }
        except Exception as e:
                return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))

    #New ENDPOINT
    @http.route('/api/get_category_hierarchy', auth='user', type='json', methods=['POST'], csrf=False)
    def get_category_hierarchy(self):
        """
            Author: nidhi@setconsulting.com
            Date: 14/08/24
            Task: Get product list {https://app.clickup.com/t/86dx1dcuc : comment --> https://app.clickup.com/t/86dx1dcuc?comment=90170141966074}
            Purpose: change {api_name,config,minutes_for_api,limit_for_api} value because client given code taking value of api_get_product_prices
        """

        api_name = 'api_get_category_hierarchy'
        config = request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.api_get_category_hierarchy')
        if config:
            minutes_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.minutes_for_api_get_category_hierarchy'))
            limit_for_api = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.limit_for_api_get_category_hierarchy'))
            _logger.info(f"Minutes for API- {api_name}: {minutes_for_api}, Limit for API- {api_name}: {limit_for_api}")
            rate_limiter = RateLimiter.get_rate_limiter(api_name, request.env)
            user_id = request.env['ir.http'].session_info().get('uid', 0)
            key = str(user_id)
            if rate_limiter.is_rate_limited(key, api_name, request.env):
                raise RateLimitExceeded()
            remaining = rate_limiter.remaining_requests(key, api_name, request.env)
            _logger.info(f"Remaining requests for api {api_name}: {remaining}")
            # 0th will be count for 0th time
        try:
            data = json.loads(request.httprequest.get_data().decode('utf-8'))
            child_category_id = data.get('category_id')

            _logger.info(f"API call for inverted hierarchy received with child_category_id: {child_category_id}")

            if not child_category_id:
                return {
                    'error': True,
                    'message': 'Please provide a valid category_id.'
                }

            # Buscar la categoría hija y sus ancestros. / Search for the child category and its ancestors.
            categories = request.env['product.category'].sudo().search([('id', 'parent_of', child_category_id)])

            if not categories:
                return {
                    'categories': []
                }

            # Usar .read() para obtener 'id', 'display_name' y 'parent_id' / Use .read() to get “id”, “display_name,” and “parent_id.”
            category_data = categories.read(['id', 'display_name', 'parent_id'])

            formatted_categories = []
            for cat in category_data:
                # La categoría raíz se identifica porque su parent_id es False. La ignoramos. / The root category is identified because its parent_id is False. We ignore it.
                #cat['parent_id'] will be False for the root category
                if not cat['parent_id']:
                    continue

                full_name = cat['display_name']
                # Elimina la primera parte del nombre jerárquico. / Remove the first part of the hierarchical name.
                name_parts = full_name.split(' / ')
                new_name = ' / '.join(name_parts[1:])

                formatted_categories.append({
                    'id': cat['id'],
                    'name': new_name
                })

            _logger.info(f"Returning {len(formatted_categories)} formatted categories.")

            # Ordenar la lista para que la categoría hija aparezca primero. / Sort the list so that the child category appears first.
            return {
                'categories': sorted(formatted_categories, key=lambda x: x['id'], reverse=True)
            }
        except Exception as e:
            _logger.error(f"An unexpected error occurred in get_category_hierarchy: {e}")
            return {'error': True, 'message': f'Invalid: {e}'}
        
    @http.route([f'{ENDPOINT}/get_product_image_link'], auth="user", type="json",
                methods=['POST'], csrf=False)
    def get_product_image_link(self) -> Dict[str, any]:
        """
            Author: jay@setuconsulting
            Date: 6/06/24
            Task: Rest API phase 2 { https://app.clickup.com/t/86dt666wc : comment --> https://app.clickup.com/t/86dt666wc?comment=90170028294265}
            Purpose: To get payment category's product image as per configuration (setting with parameter partner_id and sku)
        """
        converted_data = json.loads(request.httprequest.get_data().decode('utf-8'))
        partner_id = converted_data.get('partner_id', [])
        product_ids = converted_data.get('default_code', [])
        if not product_ids or not set(map(type, product_ids)) == {str}:
            return {
                'error': True,
                'message': 'Please enter valid json data or you must add some products to request the product stock.'
            }
        try:
            if product_ids:
                product_dictionary = []
                data = self.check_partner_info(partner_id)
                if data.get('error'):
                    return data
                prod_category_id = int(request.env['ir.config_parameter'].sudo().get_param('odoo_rest_api.product_category_id'))
                if not prod_category_id:
                    return {
                        'error': True,
                        'message': 'There are not any configure Product Category.'
                    }
                prod_cat_id = request.env['product.category'].sudo().browse(prod_category_id)
                prod_sku = request.env['product.product'].sudo().search(
                    [('categ_id', 'child_of', prod_cat_id.ids), ('sale_ok', '=', True)])
                matching_codes = [code for code in product_ids if code in prod_sku.mapped('default_code')]
                if matching_codes:
                    matching_records = [record for record in prod_sku if record.default_code in matching_codes]
                    for product_prod in matching_records:
                        product_dictionary.append({
                            "name": product_prod.name,
                            "internal_reference":product_prod.default_code,
                            "picture_link": f"/web/image?model=product.product&id={product_prod.id}&field=image_1024",
                            "extra_product_media":[f"/web/image?model=product.image&id={image.id}&field=image_1024&name={image.name}" for image in product_prod.product_template_image_ids]
                        })
                    return {"Products": product_dictionary}
                else:
                    return {
                        'error': True,
                        'message': f"There is not relevant data"
                    }
        except Exception as e:
            return RestHelper.JsonErrorResponse(_(f"Invalid: {e}"))
