from odoo import fields, models, api


class ComplexityLevels(models.Model):
    _name = 'complexity.levels'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name')
    initial_range_of_lines = fields.Integer(string='Initial range of lines')
    end_range_of_lines = fields.Integer(string='End range of lines')
    complexity_sequence = fields.Integer(string="Complexity Sequence", copy=False)