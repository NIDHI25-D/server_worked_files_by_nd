from odoo import models, fields, api, _


class TriggerThresholdLine(models.Model):
    _name = 'trigger.threshold.line'
    _description = 'Trigger Product Line'
    _order = 'sequence'

    sequence = fields.Integer(string="Sequence", default=10)
    threshold_id = fields.Many2one('trigger.threshold', string="Threshold", required=True, ondelete='cascade')

    field_1 = fields.Many2one(
        'ir.model.fields', string="Related Days",
        domain=[('model', '=', 'forecast.report.line')]
    )
    field_2 = fields.Many2one(
        'ir.model.fields', string="Compared To",
        domain=[('model', '=', 'forecast.report.line')]
    )
    change_type = fields.Selection([
        ('increase', 'Increase'),
        ('decrease', 'Decrease')
    ], string="Change Type")
    percentage = fields.Float(string="Percentage")
    logical = fields.Selection([
        ('AND', 'AND'),
        ('OR', 'OR')
    ], string="Logical Operator")
    trigger_value = fields.Float(string="Trigger Value")
    operator = fields.Selection([('<', '<'), ('<=', '≤'), ('>', '>'), ('>=', '≥')])



