import datetime
import json
import logging

from odoo import models, fields
import requests

_logger = logging.getLogger(__name__)


class SetuOracleProductVariant(models.Model):
    _name = "setu.oracle.product.variant"
    _description = "Oracle Product Product"
    _order = "sequence"

    active = fields.Boolean(string="Active", default=True)
    is_exported_in_oracle = fields.Boolean(string="Synced", default=False)

    name = fields.Char(string="Product Name", translate=True)
    title = fields.Char(string="Title", translate=True)
    default_code = fields.Char(string="SKU")
    oracle_variant_id = fields.Char(string="Variant ID")
    sequence = fields.Integer(string="Position", default=1)
    # oracle_inventory_item_id = fields.Char(string="Inventory Item ID")
    # oracle_product_create_date = fields.Datetime(string="Oracle Product Create Date")
    # oracle_product_last_updated_date = fields.Datetime(string="Oracle Product Last Updated Date")
    # oracle_last_stock_sync_date = fields.Datetime(string="Oracle Last Stock Sync Date", readonly=True)
    # oracle_last_synchronization = fields.Char(string="Last Synchronization")

    odoo_product_id = fields.Many2one("product.product", string="Odoo Product")
    setu_oracle_template_id = fields.Many2one("setu.oracle.product.template", string='Oracle Template',
                                              ondelete="cascade")
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)

    # def prepare_and_export_product_from_odoo_to_oracle(self, multi_ecommerce_connector_id, is_publish, oracle_tmpl_ids):
    #
    #     setu_process_history_obj = self.env['setu.process.history']
    #     setu_process_history_line_obj = self.env['setu.process.history.line']
    #
    #     model_id = setu_process_history_line_obj.get_model_id(self._name)
    #
    #     process_history_id = setu_process_history_obj.create_oracle_process_history("export",
    #                                                                                 multi_ecommerce_connector_id,
    #                                                                                 model_id)
    #
    #     for oracle_tmpl_id in oracle_tmpl_ids:
    #         variants = self.prepare_oracle_product_for_update_from_odoo_to_oracle(oracle_tmpl_id,
    #                                                                               multi_ecommerce_connector_id)
    #         host = self.env['setu.multi.ecommerce.connector'].browse(multi_ecommerce_connector_id.id)
    #         headers = {
    #             "accept": "text/plain",
    #             "Content-Type": "application/json-patch+json",
    #             "Authorization": f"Bearer {host.oracle_authorization}"
    #         }
    #         data = {
    #             "vendorId": host.vendor,
    #             "privateKey": host.private_key,
    #             "matchField": "SKU",
    #             "items": variants
    #         }
    #         response = requests.post(f'{host.host}/api/services/app/Vendor/RequestSyncItems', headers=headers,
    #                                  json=data)
    #         _logger.debug(f"Oracle Product Data: {data}")
    #         if response.status_code == 200:
    #             result = response.json()
    #             if result.get('result')['synchronizationId'] > 0:
    #                 oracle_tmpl_id.synchronizationId = result.get('result')['synchronizationId']
    #                 oracle_tmpl_id.last_time_template_update = datetime.datetime.now()
    #                 oracle_tmpl_id.product_published_defined = 'published_web'
    #                 oracle_tmpl_id.is_oracle_template_exported_oracle = True
    #                 message = f"For product [{oracle_tmpl_id.odoo_product_tmpl_id.default_code}] - {oracle_tmpl_id.display_name} is successfully exported and" \
    #                           f" last synchronizationId is {oracle_tmpl_id.synchronizationId}"
    #                 setu_process_history_line_obj.oracle_create_product_process_history_line(message, model_id, False,
    #                                                                                          process_history_id)
    #
    #             elif result.get('result')['isError']:
    #                 oracle_tmpl_id.last_time_template_update = datetime.datetime.now()
    #                 message = f"For product [{oracle_tmpl_id.odoo_product_tmpl_id.default_code}] - {oracle_tmpl_id.display_name} is not exported successfully and" \
    #                           f" message synchronizationId is {oracle_tmpl_id.synchronizationId}"
    #                 setu_process_history_line_obj.oracle_create_product_process_history_line(message, model_id, False,
    #                                                                                          process_history_id)
    #
    #             else:
    #                 message = f"Product [{oracle_tmpl_id.odoo_product_tmpl_id.default_code}] - {oracle_tmpl_id.display_name} is not exported at the time {datetime.datetime.now()}"
    #                 setu_process_history_line_obj.oracle_create_product_process_history_line(message, model_id, False,
    #                                                                                          process_history_id)
    #         else:
    #             pass
    #         self._cr.commit()
    #     if not process_history_id.process_history_line_ids:
    #         process_history_id.unlink()
    #     return True
    #
    # def prepare_oracle_product_for_update_from_odoo_to_oracle(self, oracle_tmpl_id, multi_ecommerce_connector_id):
    #     variants = []
    #     for variant in oracle_tmpl_id.setu_oracle_product_variant_ids:
    #         variants.append(self.oracle_prepare_variant_vals(multi_ecommerce_connector_id, variant))
    #     return variants
    #
    # def oracle_prepare_variant_vals(self, multi_ecommerce_connector_id, variant):
    #     locations = multi_ecommerce_connector_id._get_oracle_location_type()
    #     total_available_stock = variant.odoo_product_id.with_context(location=locations)._compute_quantities_dict(False,
    #                                                                                                               False,
    #                                                                                                               False)
    #     total_available_stock = total_available_stock.get(variant.odoo_product_id.id)
    #     product_stock = False
    #     if multi_ecommerce_connector_id.stock_field_id.name == "free_qty":
    #         product_stock = total_available_stock.get('qty_available')
    #     elif multi_ecommerce_connector_id.stock_field_id.name == "virtual_available":
    #         product_stock = total_available_stock.get('virtual_available')
    #     elif multi_ecommerce_connector_id.stock_field_id.name == 'outgoing_qty':
    #         product_stock = total_available_stock.get('free_qty')
    #
    #     available_stock = int(product_stock * multi_ecommerce_connector_id.stock_percentage / 100)
    #     if available_stock >= multi_ecommerce_connector_id.minimum_stock_quantities:
    #         stock_to_upload = available_stock
    #     else:
    #         stock_to_upload = 0
    #     pricelist_price = multi_ecommerce_connector_id.odoo_pricelist_id._get_product_price(variant.odoo_product_id,
    #                                                                                         stock_to_upload)
    #
    #     return {
    #         "upc": "",
    #         "sku": variant.odoo_product_id.default_code,
    #         "stock": stock_to_upload,
    #         "cost": pricelist_price,
    #         "currency": variant.odoo_product_id.currency_id.name
    #     }
    #
    # def oracle_export_product_log_line(self, message, model_id, process_history_id):
    #     setu_process_history_line_obj = self.env['setu.process.history.line']
    #     vals = {"message": message, "model_id": model_id,
    #             "process_history_id": process_history_id.id if process_history_id else False}
    #     setu_process_history_line_obj.create(vals)
    #     return True
