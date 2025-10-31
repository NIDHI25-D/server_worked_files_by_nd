from odoo import fields, models


class RamMemoryCapacity(models.Model):
    _name = 'ram.memory.capacity'
    _description = 'Ram Memory Capacity'

    name = fields.Char()
