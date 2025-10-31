# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ScoreConfLineQTY(models.Model):
    _name = "score.conf.line.qty"
    _description = "Score Conf Line Qty"

    from_quantity = fields.Float(string="From Quantity")
    to_quantity = fields.Float(string="To Quantity")
    pre_score = fields.Integer(string="Pre Score")

    score_conf_id = fields.Many2one(comodel_name="score.conf", ondelete='cascade', copy=False)

    calculation_based_on = fields.Selection(related='score_conf_id.calculation_based_on')
