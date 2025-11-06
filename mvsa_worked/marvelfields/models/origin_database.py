from odoo import fields, models, api


class OriginDatabase(models.Model):
    _name = 'origin.database'
    _description = 'Origin Database'
    _rec_name = "origin"

    origin = fields.Char(string='Origin', required=True)
