from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    preferred_delivery_method_ids = fields.Many2many('delivery.carrier', string="Preferred Delivery Method")
    shipping_carrier_ids = fields.Many2many(related='property_delivery_carrier_id.shipping_carrier_ids',
                                           string='Carrier')
    package_partner_id = fields.Many2one('shipping.carrier', string="Package")
    pallet_partner_id = fields.Many2one('shipping.carrier', string="Pallet")
    overdimensioned_partner_id = fields.Many2one('shipping.carrier', string="Overdimensioned")

    @api.onchange('property_delivery_carrier_id')
    def onchange_method_to_assign_property_delivery_carrier_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 06/01/25
            Task: Migration from V16 to V18
            Purpose: When property_delivery_carrier_id is changed, then related fields should be false
        """
        res = {}
        if self.property_delivery_carrier_id:
            for records in self:
                records.package_partner_id = False
                records.pallet_partner_id = False
                records.overdimensioned_partner_id = False
        return res
