from odoo import models, _, fields
from datetime import datetime
from odoo.exceptions import ValidationError
import requests
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mirakl_order_status = fields.Char(string="Mirakl Order Status", copy=False)
    is_mirakl_sale_order = fields.Boolean(string="Is Mirakl Sale Order ?", default=False, copy=False)
    mirakl_order_id = fields.Char(string="Mirakl Order ID", copy=False)
    setu_mirakl_payment_gateway_id = fields.Many2one('setu.mirakl.payment.gateway', string="Mirakl Payment Gateway",
                                                     copy=False)

    def mirakl_create_import_specific_order_chain(self, multi_ecommerce_connector_id, order_ids):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method is used to import the sale order of the respective Coppel ID.
                     It will create the Partner if it not there.
        """
        setu_process_history_obj_mirakl = self.env['setu.process.history']
        setu_process_history_line_obj_mirakl = self.env['setu.process.history.line']
        order_vals = {}
        headers = {
            'accept': 'application/json',
            'Authorization': multi_ecommerce_connector_id.mirakl_api_key,
            'Content-Type': 'application/json',
        }
        url = f"{multi_ecommerce_connector_id.mirakl_host}/api/orders"
        query = {
            "order_ids": order_ids,
        }
        try:
            response = requests.get(url, headers=headers, params=query)
            data = response.json()
            if response.status_code == 200 and data.get("orders"):
                res_partner_obj = self.env['res.partner']
                for order in data.get("orders", []):

                    # Process history
                    model_id = setu_process_history_line_obj_mirakl.get_model_id("sale.order")
                    process_history_id = setu_process_history_obj_mirakl.create_mirakl_process_history("import",
                                                                                                       multi_ecommerce_connector_id,
                                                                                                       model_id)

                    # Import Order After Date
                    if datetime.strptime(order.get("created_date"),
                                         '%Y-%m-%dT%H:%M:%SZ') < multi_ecommerce_connector_id.import_mirakl_order_from:
                        message = "Mirakl Order: %s is not import due to missing configuration of Import Order After Date %s" % (
                            order.get("order_id"), datetime.strptime(order.get("created_date"), '%Y-%m-%dT%H:%M:%SZ'))
                        setu_process_history_line_obj_mirakl.mirakl_prepare_process_history_line_vals(message,model_id,process_history_id,order.get('order_id'))
                        continue

                    if not process_history_id.process_history_line_ids:
                        process_history_id.unlink()

                    sale_order_search_rec = self.search(
                        [('mirakl_order_id', '=', order.get('order_id')), ('is_mirakl_sale_order', '=', True)])

                    if sale_order_search_rec:
                        raise ValidationError(_("This Sale order Already exist as : %s",sale_order_search_rec.name))
                    customer_data = order.get('customer')
                    partner = res_partner_obj.search([
                        ('name', 'ilike', f"{customer_data.get('firstname')} {customer_data.get('lastname')}"),
                    ], limit=1)
                    payment_gateway_obj_mirakl = self.env["setu.mirakl.payment.gateway"]
                    mirakl_payment_gateway_obj = payment_gateway_obj_mirakl.find_and_create_mirakl_payment_gateway(
                        multi_ecommerce_connector_id, order)
                    partner.find_existing_mirakl_customer(int(customer_data.get('customer_id')),
                                                          multi_ecommerce_connector_id)
                    if not partner:
                        partner = partner.create_main_mirakl_customer(multi_ecommerce_connector_id, order)
                        partner.update({
                            'type': 'contact',
                            'is_customer_from_mirakl': True,
                            'mirakl_customer_id': customer_data.get('customer_id'),
                        })
                        partner_shipping_obj = self.env['res.partner']
                        partner_shipping = partner_shipping_obj.create_main_mirakl_customer(multi_ecommerce_connector_id,
                                                                                            order)
                        partner_shipping.update({
                            'type': 'delivery',
                            'parent_id': partner.id,
                        })
                    else:
                        partner_delivery_address = partner.search(
                            [('parent_id', '=', partner.id), ('type', '=', 'delivery')], limit=1)
                        if not partner_delivery_address:
                            partner.partner_shipping_id = customer_data.get('shipping_address').id
                            partner = partner.create_main_mirakl_customer(multi_ecommerce_connector_id, order)
                            partner.update({
                                'type': 'delivery',
                                'parent_id': partner.id,
                            })
                    order_vals.update({
                        'partner_id': partner.id,
                        'date_order': datetime.strptime(order.get("created_date"), '%Y-%m-%dT%H:%M:%SZ'),
                        'currency_id': self.env['res.currency'].search([('name', '=', order.get("currency_iso_code"))],
                                                                       limit=1).id,
                        'warehouse_id': multi_ecommerce_connector_id.odoo_warehouse_id.id,
                        'multi_ecommerce_connector_id': multi_ecommerce_connector_id.id,
                        'order_line': [],
                        'mirakl_order_status': order.get("order_state"),
                        'mirakl_order_id': order.get('order_id'),
                        'setu_mirakl_payment_gateway_id': mirakl_payment_gateway_obj.id,
                        'customer_confirmation_date': datetime.now(),
                        'is_mirakl_sale_order': True,
                        'user_id': multi_ecommerce_connector_id.user_id.id,
                        'team_id': multi_ecommerce_connector_id.crm_team_id.id,
                        'partner_shipping_id': partner.search([('parent_id', '=', partner.id), ('type', '=', 'delivery')],
                                                              limit=1).id,
                        'partner_invoice_id': multi_ecommerce_connector_id.partner_invoice_id.id,
                        'pricelist_id': multi_ecommerce_connector_id.odoo_pricelist_id.id,
                    })
                    if not multi_ecommerce_connector_id.is_use_odoo_order_prefix:
                        if multi_ecommerce_connector_id.order_prefix:
                            name = "%s%s" % (multi_ecommerce_connector_id.order_prefix, order.get("order_id"))
                        else:
                            name = order.get("order_id")
                        order_vals.update({"name": name})

                    for order_line in order.get("order_lines"):
                        product = self.env['product.product'].search(
                            [('default_code', '=', order_line.get('product_shop_sku'))])
                        if product:
                            order_line_vals = {
                                'product_id': product.id,
                                'product_uom_qty': order_line.get('quantity'),
                            }
                            order_vals['order_line'].append((0, 0, order_line_vals))
                if order_vals and order_vals['order_line']:
                    # Create the sale order
                    created_sale_order = self.create(order_vals)
                    _logger.info(f"Mirakl Sale order--> {created_sale_order},{created_sale_order.name}")
                    if order.get('order_state') == 'SHIPPING':  # Awaiting shipment = SHIPPING : paid -> Confirm and Lock
                        created_sale_order.action_confirm()
                        _logger.info(
                            f"Mirakl Sale order--> {created_sale_order.name} is changed to state : {created_sale_order.state}")
                    elif order.get('order_state') == 'WAITING_DEBIT_PAYMENT':  # Debit in progress :  pending -> Quotation
                        created_sale_order.state = 'draft'
                        _logger.info(
                            f"Mirakl Sale order--> {created_sale_order.name} is changed to state : {created_sale_order.state}")
                    else:
                        _logger.info(
                            f"Mirakl Sale order's order_state from API was--> {order.get('order_state')}, for Sale order --> {created_sale_order.name}")
                        created_sale_order.state = 'draft'
                    self.mirakl_document_creation(multi_ecommerce_connector_id,headers,created_sale_order)
                    return created_sale_order

            else :
                _logger.info(
                    f"Mirakl Sale order Error for ID: --> {order_ids} with  Code : {response.status_code}")
                return {
                    'code': response.status_code,
                    'message': response.text,
                }
        except Exception as e:
            raise ValidationError(str(e))

    def mirakl_document_creation (self,multi_ecommerce_connector_id,headers,order_id) :
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method consist the API of :
                    OR72 - Lists order's documents (this is used to get documents of the order) &
                    OR73 - Download one or multiple documents attached to one or multiple orders (this is used to get the document of selected document_id)
                    Creates the attachment and added in the respective sale order.
        """
        document_endpoint = f'{multi_ecommerce_connector_id.mirakl_host}/api/orders/documents'
        query = {
            "order_ids": order_id.mirakl_order_id,
        }
        try :
            document_response = requests.get(document_endpoint, headers=headers,params=query)
            if document_response.status_code == 200:
                response_byte_to_json = json.loads(document_response.content.decode('utf-8'))
                shipping_label_found = False
                for json_data in response_byte_to_json.get('order_documents',[]):
                    if json_data.get('type') == 'SHIPPING_LABEL':
                        shipping_label_found = True
                        document_id = json_data.get('id')
                        download_one_multiple_docs_endpoint = f'{multi_ecommerce_connector_id.mirakl_host}/api/orders/documents/download'
                        query = {
                            "document_ids": document_id,
                        }
                        try:
                            doc_download = requests.get(download_one_multiple_docs_endpoint, headers=headers, params=query)
                            if doc_download.status_code == 200 :
                                attachment = self.env['ir.attachment'].create({
                                    'name': "Mirakl_" + json_data.get('file_name'),
                                    'type': 'binary',
                                    'datas': base64.b64encode(doc_download.content),
                                    'mimetype': 'application/pdf',
                                    'res_model': 'sale.order',
                                    'res_id': order_id.id
                                })
                                order_id.message_post(
                                    body="Mirakl Attachment",
                                    attachments=[("Mirakl_" + json_data.get('file_name'), doc_download.content)]
                                )
                                _logger.info(f"Mirakl attachment --> {attachment} is created and its attached within the Sale order : {order_id.name}")
                                return attachment

                        except Exception as e:
                            raise ValidationError(str(e))
                # If no shipping label was found, log it
                if not shipping_label_found:
                    _logger.warning(f"No shipping label found for Mirakl Order ID: {order_id.mirakl_order_id}")

        except Exception as e:
            raise ValidationError(str(e))