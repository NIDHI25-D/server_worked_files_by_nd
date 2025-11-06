from odoo import fields, models, api

class HardDiskLine(models.Model):
    _name = 'hard.disk.line'
    _description = 'Hard Disk line'

    asset_id = fields.Many2one('account.asset')
    hard_disk_type_id = fields.Many2one('hard.disk.type')
    hard_disk_capacity_ids = fields.Many2many('hard.disk.capacity', 'hard_disk_capacity_relation')
