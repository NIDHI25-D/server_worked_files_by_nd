from odoo import fields, models


class CombustiblePinType(models.Model):
    _name = 'combustible.pin.type'
    _description = "CombustiblePinType"

    name = fields.Char(index='trigram')
