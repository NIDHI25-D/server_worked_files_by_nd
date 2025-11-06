from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    display_message_on_website = fields.Char(string="Display Message On Website")
