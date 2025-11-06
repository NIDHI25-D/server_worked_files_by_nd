from odoo import fields, models


class OperativeSystemType(models.Model):
    _name = 'operative.system.type'
    _description = 'Operative System Type'

    name = fields.Char()
