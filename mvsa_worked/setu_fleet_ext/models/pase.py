from odoo import fields, models


class PaseTags(models.Model):
    _name = 'pase.tag'
    _description = "PaseTags"

    name = fields.Char(index='trigram')
