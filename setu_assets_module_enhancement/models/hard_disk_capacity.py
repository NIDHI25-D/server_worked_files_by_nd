from odoo import fields, models


class HardDiskCapacity(models.Model):
    _name = 'hard.disk.capacity'
    _description = 'Hard Disk Capacity'

    name = fields.Char()
    asset_id = fields.Many2one('account.asset')
