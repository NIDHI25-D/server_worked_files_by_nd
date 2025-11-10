from odoo import models, fields, api,_

class TriggerMain(models.Model):
    _name = 'trigger.main'
    _description = 'Main Trigger Logic'

    name = fields.Char(string='Name', required=True)
    trigger_main_domain = fields.Char(string="Trigger Domain")

    threshold_line_ids = fields.One2many('trigger.threshold', 'trigger_id', string='Threshold Lines')
    trigger_color = fields.Selection([
        ('danger', 'Red (Danger)'),
        ('warning', 'Orange (Warning)'),
        ('success', 'Green (Success)'),
        ('info', 'Blue (Info)'),
    ], string="Trigger Color", default='info')
    row_color = fields.Char(string="Row Color", help="Select a color for rows triggered by this rule")
