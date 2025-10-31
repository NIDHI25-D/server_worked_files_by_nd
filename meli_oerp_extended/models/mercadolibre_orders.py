import base64

import requests
from odoo.exceptions import MissingError

from odoo import models, _, api


class MercadolibreOrders(models.Model):
    _inherit = 'mercadolibre.orders'

    def get_shipping_receipt(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18
              Purpose: for post-message of shipment labels from MELI.
        """
        if self:
            order_id = self
        else:
            order_id = self.browse(self._context.get('active_id'))
        company_id = self.env.company
        bearer_token = company_id.mercadolibre_access_token
        headers = {
            "accept": "text/plain",
            "Content-Type": "application/json-patch+json",
            "Authorization": f"Bearer {bearer_token}"
        }
        response = requests.get(f'https://api.mercadolibre.com/shipment_labels?shipment_ids={order_id.shipping_id}&savePdf=Y',
                                 headers=headers)
        if response.status_code in [200, 201]:
            attachment = False
            if response.content:
                attachment = self.env['ir.attachment'].create({
                    'name': "Shipping_"+str(order_id.shipping_id)+".pdf",
                    'type': 'binary',
                    'datas': base64.b64encode(response.content),
                    'mimetype': 'application/pdf',
                    'res_model': 'mercadolibre.orders',
                    'res_id': order_id.id
                })
            order_id.message_post(attachment_ids=[attachment.id])
        else:
            order_id.message_post(body='The shipping label pdf is not generated the order.')
            # raise MissingError(_("The shipping label pdf is not generated this order."))
        return {}

    @api.model_create_multi
    def create(self, values):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18
              Purpose: for post-message of shipment labels from MELI.
        """
        res = super().create(values)
        for record in res:
            record.get_shipping_receipt()
        return res
