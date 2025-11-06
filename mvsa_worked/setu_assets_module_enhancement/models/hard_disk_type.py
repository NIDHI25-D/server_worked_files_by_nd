from odoo import fields, models


class HardDiskType(models.Model):
    _name = 'hard.disk.type'
    _description = 'Hard Disk Type'

    name = fields.Char()
    hard_disk_capacity_ids = fields.Many2many('hard.disk.capacity')
