# -*- coding: utf-8 -*-
import datetime
from datetime import datetime

from odoo import fields, models


class InvSessionDetails(models.Model):
    _name = 'inventory.session.details'
    _description = 'Inventory Session Details'

    duration = fields.Char(compute="_compute_duration", string="Duration")

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")

    duration_seconds = fields.Integer(compute="_compute_duration", string="Duration seconds")

    session_id = fields.Many2one(comodel_name="setu.inventory.count.session", string="Session")

    def _compute_duration(self):
        for history in self:
            start_date = history.start_date
            end_date = history.end_date
            if not history.end_date:
                end_date = datetime.now()
            difference = end_date - start_date
            history.duration = difference
            history.duration_seconds = int(difference.seconds)
