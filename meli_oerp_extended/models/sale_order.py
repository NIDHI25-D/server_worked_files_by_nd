from odoo import api, fields, models
import base64
from datetime import datetime

import requests
import logging
_logger = logging.getLogger("meli_oerp_extended_SaleOrder")


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    confirm_shipment = fields.Datetime(string="Confirm Shipment")

    def set_confirm_shipment(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18 (https://app.clickup.com/t/86dub42p4)
              Purpose: Create a "Confirm Shipment" field for the same
              functionality as the "customer confirmation date" field for mercadolibre sale order.
        """
        for record in self:
            record.confirm_shipment = datetime.now()

    def get_shipping_receipt(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18
              Purpose: for post-message of shipment labels from MELI.
        """
        if self:
            order = self
        else:
            order = self.browse(self._context.get('active_ids')) if len(
                self._context.get('active_ids')) > 1 else self.browse(self._context.get('active_id'))
        for order_id in order:
            if not order_id.meli_shipping_id:
                continue
            company_id = self.env.company
            bearer_token = company_id.mercadolibre_access_token
            headers = {
                "accept": "text/plain",
                "Content-Type": "application/json-patch+json",
                "Authorization": f"Bearer {bearer_token}"
            }
            response = requests.get(
                f'https://api.mercadolibre.com/shipment_labels?shipment_ids={order_id.meli_shipping_id}&savePdf=Y',
                headers=headers)
            if response.status_code in [200, 201]:
                attachment = False
                if response.content:
                    attachment = self.env['ir.attachment'].create({
                        'name': "Shipping_" + str(order_id.meli_shipping_id) + ".pdf",
                        'type': 'binary',
                        'datas': base64.b64encode(response.content),
                        'mimetype': 'application/pdf',
                        'res_model': 'sale.order',
                        'res_id': order_id.id
                    })
                order_id.message_post(attachment_ids=[attachment.id])
            else:
                order_id.message_post(body='The shipping label pdf is not generated the order.')
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
            if record.meli_shipping_id:
                record.get_shipping_receipt()
        return res

    def action_confirm(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18 (https://app.clickup.com/t/86dv9e3z2)
              Purpose:  setting the responsible person in order picking if
              meli_shipment_logistic_type = 'fulfillment'
        """
        res = super(SaleOrder, self).action_confirm()
        for order_id in self:
            if order_id.meli_order_id and order_id.meli_shipment_logistic_type == 'fulfillment':
                company_id = self.env.company
                if company_id.responsible_person and hasattr(order_id.picking_ids, 'responsible_person'):
                    for picking_id in order_id.picking_ids._origin:
                        picking_id.sudo().write({'responsible_person': company_id.responsible_person.id})
                        _logger.info(f"responsible person is updated for {picking_id.name}")
        return res
