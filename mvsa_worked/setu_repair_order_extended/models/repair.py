
from odoo import models, fields, api


class RepairStateCTB(models.Model):
    _name = 'repair.state.ctb'
    _rec_name = 'value'
    _order = 'sequence'
    _description = "Repair State Ctb"

    sequence = fields.Integer(string="Sequence")
    key = fields.Char(string='Key')
    value = fields.Char(string='Value')
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
