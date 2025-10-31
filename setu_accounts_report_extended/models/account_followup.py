# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import timedelta


class FollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'

    active = fields.Boolean(default=True, string="Active")