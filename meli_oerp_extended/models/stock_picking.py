import base64

import requests
from odoo.exceptions import UserError

from odoo import fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipment_logistic_type = fields.Char(related='sale_id.meli_shipment_logistic_type')
    confirm_shipment = fields.Datetime(related='sale_id.confirm_shipment',store=True)

    #https://app.clickup.com/t/86dt4vwxa
    def get_shipping_receipt(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18
              Purpose: for post-message of shipment labels from MELI.
        """
        picking_id = self.browse(self._context.get('active_id'))
        if not picking_id.sale_id:
            raise UserError(_("This transfer does not contain sale order reference."))
        for order_id in picking_id.sale_id:
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
                        'res_model': 'stock.picking',
                        'res_id': picking_id.id
                    })
                picking_id.message_post(attachment_ids=[attachment.id])
            else:
                picking_id.message_post(body='The shipping label pdf is not generated.')
        return {}
