from odoo import api, fields, models, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    shipping_carrier_ids = fields.Many2many(
        'shipping.carrier',
        relation="shipping_carrier_dependencies_rel",
        column1="shipping_carrier_id", column2="carrier_id",
        string='Carriers')
    is_display_carrier_on_website = fields.Boolean(
        string='Display Carrier On Website',
        required=False)

    def _match_address(self, partner):
        """
            Author: jay.garach@setuconsulting.com
            Date: 31/12/24
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86dqut9z1)
            Purpose: remove a shipping method if partner is excluded for the shipping method
        """
        if partner.preferred_delivery_method_ids and self not in partner.preferred_delivery_method_ids:
            return False
        return super(DeliveryCarrier, self)._match_address(partner)
