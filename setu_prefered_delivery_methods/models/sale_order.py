from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_carrier_id = fields.Many2one('shipping.carrier')

    def action_confirm(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 06/01/25
            Task: Migration from V16 to V18
            Purpose: if delivery_set is not set then have to raise error or if this from multi_ecommerce_connector_id
            or a mercadolibre order then have to bypass the error.
        """
        if self.delivery_set or self.meli_shipment.order or self.multi_ecommerce_connector_id:
            return super().action_confirm()
        else:
            raise UserError(_('Shipping method is not selected for this order.'))
