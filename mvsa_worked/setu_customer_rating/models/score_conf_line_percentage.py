# -*- coding: utf-8 -*-
from odoo import fields, models, _

class ScoreConfLinePercentage(models.Model):
    _name = "score.conf.line.percentage"
    _description = "Score Conf Line Percentage"

    from_percentage = fields.Float(string="From Percentage")
    to_percentage = fields.Float(string="To Percentage")
    pre_score = fields.Integer(string="Pre Score")

    score_conf_id = fields.Many2one(
        comodel_name="score.conf",
        ondelete='cascade', copy=False)

    calculation_based_on = fields.Selection(related="score_conf_id.calculation_based_on")
