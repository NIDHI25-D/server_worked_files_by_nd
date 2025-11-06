# -*- coding: utf-8 -*-
from odoo import api, fields, models

class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    humand_allocation_id = fields.Integer(string="Humand Allocation Id")