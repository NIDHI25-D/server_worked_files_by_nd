from odoo import models, fields, api, _


class PriceBase(models.Model):
    _name = 'price.bases'
    _description = 'price.bases'

    day_start = fields.Integer(string="Date Start", required=True)
    day_end = fields.Integer(string="Date End", required=True)
    discount = fields.Float(string="Discount")
    competition_level_id = fields.Many2one('competition.level', string="Competition Level")
