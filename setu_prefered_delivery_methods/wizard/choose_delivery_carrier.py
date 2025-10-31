from odoo import api, fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    shipping_carrier_id = fields.Many2one(
        comodel_name='shipping.carrier',
        string='Carrier')
    shipping_carrier_ids = fields.Many2many(related='carrier_id.shipping_carrier_ids')

    def button_confirm(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 07/01/25
            Task: Migration from V16 to V18
            Purpose: setting the shipping carrier while confirming shipping.
        """
        res = super().button_confirm()
        self.order_id.write({
            'shipping_carrier_id': self.shipping_carrier_id.id,
        })
        return res
