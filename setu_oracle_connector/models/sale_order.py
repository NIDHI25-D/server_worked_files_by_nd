import base64
from datetime import datetime

import pandas as pd
import pytz
import requests

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_oracle_order = fields.Boolean('Oracle Order')
    oracle_internal_id = fields.Integer('Oracle Internal Id')
    oracle_transaction_id = fields.Integer('Oracle Transaction Id')
    oracle_order_status = fields.Char('Oracle Order Status')

    # def cron_auto_import_oracle_order(self, ctx):
    #     multi_ecommerce_connector_id = ctx.get('multi_ecommerce_connector_id')
    #     setu_process_history_obj = self.env['setu.process.history']
    #     setu_process_history_line_obj = self.env['setu.process.history.line']
    #     model_id = setu_process_history_line_obj.get_model_id(self._name)
    #     connector_id = self.env['setu.multi.ecommerce.connector'].browse(multi_ecommerce_connector_id)
    #     process_history_id = setu_process_history_obj.create_oracle_process_history("import",
    #                                                                                 connector_id,
    #                                                                                 model_id)
    #
    #     headers = {
    #         "accept": "text/plain",
    #         "Content-Type": "application/json-patch+json",
    #         "Authorization": f"Bearer {connector_id.oracle_authorization}"
    #     }
    #     data = {
    #         "vendorId": connector_id.vendor,
    #         "privateKey": connector_id.private_key,
    #         "status": "Pending Receipt"
    #     }
    #     response = requests.post(f'{connector_id.host}/api/services/app/Vendor/Orders', headers=headers,
    #                              json=data)
    #     chain_order_lst = []
    #     orders = []
    #     if response.status_code in (200, 201):
    #         result = response.json()
    #         result = pd.DataFrame(result.get('result'))
    #         sorted_value = result.sort_values(by='internalId', ignore_index=True)
    #         last_sl_order_id = self.search([('multi_ecommerce_connector_id', '=', connector_id.id)], order='id desc',
    #                                        limit=1)
    #         if last_sl_order_id:
    #             sorted_value = sorted_value[sorted_value['internalId'] > last_sl_order_id.oracle_internal_id]
    #             for vals in sorted_value.to_dict('records'):
    #                 orders.append(self._prepare_oracle_sale_order_values(connector_id, vals))
    #         else:
    #             for vals in sorted_value.to_dict('records'):
    #                 orders.append(self._prepare_oracle_sale_order_values(connector_id, vals))
    #         sale_orders = self.create(orders)
    #         for order in sale_orders:
    #             order._compute_warehouse_id()
    #             # order.action_update_prices()
    #         chain_order_lst.append(sale_orders.mapped('oracle_internal_id'))
    #         message = f"Sales order {sale_orders.mapped('name')} - {chain_order_lst} are successfully imported."
    #         setu_process_history_line_obj.oracle_create_sale_order_process_history_line(message, model_id, False,
    #                                                                                     process_history_id)
    #     else:
    #         message = f"Something went wrong when importing the sale orders. It response the {response.status_code} code."
    #         setu_process_history_line_obj.oracle_create_sale_order_process_history_line(message, model_id, False,
    #                                                                                     process_history_id)
    #     return chain_order_lst
    #
    # def _prepare_oracle_sale_order_values(self, connector_id, vals):
    #     order_date = pytz.timezone("America/Mexico_City").localize(
    #         datetime.strptime(vals.get('tranDate'), "%m/%d/%Y %H:%M:%S %p"), is_dst=None).astimezone(
    #         pytz.utc).strftime("%m/%d/%Y %I:%M:%S %p")
    #     tax_value = next((item for item in vals.get('items') if item["quantity"] == -1), None)
    #     rate_with_percentage = int(tax_value.get('rate').strip('%'))
    #     if rate_with_percentage == 0:
    #         tax_value['name'] = 'IVA(0%)'
    #     elif rate_with_percentage == 16:
    #         tax_value['name'] = 'IVA(16%)'
    #     tax_value_id = self.env['account.tax'].search(
    #         [('description', 'like', tax_value['name']), ('amount', '=', rate_with_percentage),
    #          ('type_tax_use', '=', 'sale')])
    #
    #     order_vals = {
    #         'partner_id': connector_id.oracle_partner_id.id,
    #         'is_oracle_order': True,
    #         'date_order': datetime.strptime(order_date, "%m/%d/%Y %H:%M:%S %p"),
    #         'oracle_internal_id': vals.get('internalId'),
    #         'oracle_transaction_id': int(vals.get('tranId')),
    #         'oracle_order_status': vals.get('status'),
    #         'multi_ecommerce_connector_id': connector_id.id,
    #         'pricelist_id': connector_id.odoo_pricelist_id.id,
    #         'order_line': [(0, 0, {
    #             'oracle_upc': item['upc'],
    #             'product_id': self.env['product.product'].search([('default_code', '=', item['global_SKU'])]).id,
    #             'product_uom_qty': item['quantity'],
    #             'price_unit': float(item['rate']),
    #             'tax_id': [tax.id for tax in tax_value_id]
    #         }) for item in vals['items'] if item['global_SKU']]
    #     }
    #     return order_vals
    #
    # def action_confirm(self):
    #     res = super().action_confirm()
    #     if self.multi_ecommerce_connector_id and self.ecommerce_connector == 'oracle_connector':
    #         setu_process_history_obj = self.env['setu.process.history']
    #         setu_process_history_line_obj = self.env['setu.process.history.line']
    #         model_id = setu_process_history_line_obj.get_model_id(self._name)
    #         process_history_id = setu_process_history_obj.create_oracle_process_history("import",
    #                                                                                     self.multi_ecommerce_connector_id,
    #                                                                                     model_id)
    #         headers = {
    #             "accept": "text/plain",
    #             "Content-Type": "application/json-patch+json",
    #             "Authorization": f"Bearer {self.multi_ecommerce_connector_id.oracle_authorization}"
    #         }
    #         data = {
    #             "vendorId": self.multi_ecommerce_connector_id.vendor,
    #             "privateKey": self.multi_ecommerce_connector_id.private_key,
    #             "status": "Pending Receipt",
    #             "internalId": self.oracle_internal_id
    #         }
    #         response = requests.post(f'{self.multi_ecommerce_connector_id.host}/api/services/app/Vendor/OrderGuide',
    #                                  headers=headers, json=data)
    #         if response.status_code in (200, 201):
    #             result = response.json()
    #             pdf_file = result['result']['urlAwb']
    #             if pdf_file:
    #                 get_pdf = requests.get(pdf_file)
    #                 if get_pdf.status_code in (200, 201):
    #                     attachment = self.env['ir.attachment'].create({
    #                         'name': "Oracle_" + str(self.oracle_internal_id) + ".pdf",
    #                         'type': 'binary',
    #                         'datas': base64.b64encode(get_pdf.content),
    #                         'mimetype': 'application/pdf',
    #                         'res_model': 'sale.order',
    #                         'res_id': self.id
    #                     })
    #                     message = f"Sales order {self.name} - {self.oracle_internal_id} is successfully imported."
    #                     setu_process_history_line_obj.oracle_create_attachment_process_history_line(message, model_id,
    #                                                                                                 False,
    #                                                                                                 process_history_id)
    #                     self.message_post(attachment_ids=[attachment.id])
    #         else:
    #             self.message_post(
    #                 body=f"For the internalId of this order [{self.oracle_internal_id}] no delivery guide found.")
    #             message = f"For the internalId {self.oracle_internal_id} no delivery guide found."
    #             setu_process_history_line_obj.oracle_create_attachment_process_history_line(message, model_id,
    #                                                                                         False,
    #                                                                                         process_history_id)
    #     return res
