from odoo import api, fields, models


class ShippingCarrier(models.Model):
    _name = 'shipping.carrier'

    name = fields.Char('name')
    delivery_carrier_id = fields.Many2one('delivery.carrier')
    active = fields.Boolean(default=True)
