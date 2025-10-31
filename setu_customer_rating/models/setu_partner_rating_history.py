# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SetuPartnerRatingHistory(models.Model):
    _name = "setu.partner.rating.history"
    _description = "Partner Rating History"

    # Datetime Fields
    date_changed = fields.Datetime(string="Date Change", required=False)

    # Integer Fields
    previous_total_score = fields.Integer(string="Previous Total Score",default=0)
    current_total_score = fields.Integer(string="Current Total Score",default=0)

    # Relational Fields
    previous_customer_rating_id = fields.Many2one(
        comodel_name="customer.rating",
        string="Previous Customer Rating", required=False)
    current_customer_rating_id = fields.Many2one(
        comodel_name="customer.rating",
        string="Current Customer Rating", required=False)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",required=False)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company", required=False)
    customer_score_id = fields.Many2one(
        comodel_name="customer.score",
        string="Customer score")







