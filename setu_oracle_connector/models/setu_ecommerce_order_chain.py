from datetime import datetime, timedelta

import pandas as pd
import requests

from odoo import models


class SetuEcommerceOrderChain(models.Model):
    _inherit = 'setu.ecommerce.order.chain'

    # def oracle_connector_import_ecommerce_order_chain(self, multi_ecommerce_connector_id):
    #     from_date = multi_ecommerce_connector_id.last_unshipped_order_import
    #     to_date = datetime.now()
    #     if not from_date:
    #         from_date = datetime.now() - timedelta(3)
    #     self.oracle_master_create_order_chain_line(multi_ecommerce_connector_id, from_date, to_date,
    #                                                 record_created_from="scheduled_action")
    #     return True
    #
    # def oracle_master_create_order_chain_line(self, multi_ecommerce_connector_id, from_date, to_date,
    #                                            record_created_from="scheduled_action"):
    #     chain_order_lst = []
    #     connector_id = self.env['setu.multi.ecommerce.connector'].browse(multi_ecommerce_connector_id.id)
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
    #     if response.status_code == 200:
    #         result = response.json()
    #         result = pd.DataFrame(result.get('result'))
    #         for order in result['result']:
    #             print(order)
    #     return chain_order_lst
