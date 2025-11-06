from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    is_mostrador_delivery = fields.Boolean(string="Is Mostrador Delivery")
