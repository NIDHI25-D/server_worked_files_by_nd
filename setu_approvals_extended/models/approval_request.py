from odoo import models, fields, api, _
from datetime import datetime
import re


class Approvals(models.Model):
    _inherit = 'approval.request'

    current_approver_id = fields.Many2one('res.users')
    # is_enable = fields.Boolean(compute='_get_setting_variable')
    description_normalize = fields.Text(string="Description Normalize")
