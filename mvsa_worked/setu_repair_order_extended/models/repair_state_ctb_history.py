from odoo import models, fields, api


class RepairStateCtbHistory(models.Model):
    _name = 'repair.state.ctb.history'
    _order = 'id asc'
    _description = "Repair State Ctb History"

    repair_state_ctb_id = fields.Many2one('repair.state.ctb', string="Repair State CTB")
    repair_order_id = fields.Many2one('repair.order', string="Repair Order")
