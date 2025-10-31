from odoo import fields, models


class RamMemoryType(models.Model):
    _name = 'ram.memory.type'
    _description = 'Ram Memory Type'

    name = fields.Char()
