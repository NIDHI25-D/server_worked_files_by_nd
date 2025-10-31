from odoo import api, fields, models


class ShippingIncident(models.Model):
    _name = 'shipping.incident'

    name = fields.Char('name')
    color = fields.Integer('Color', default=0)