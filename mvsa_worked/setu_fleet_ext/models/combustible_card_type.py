from odoo import models, fields


class CombustibleCardType(models.Model):
    _name = 'combustible.card.type'
    _description = "CombustibleCardType"

    name = fields.Char(index='trigram')
