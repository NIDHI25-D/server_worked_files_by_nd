from odoo import models, fields, api


class SetuAttendance(models.Model):
    _inherit = 'hr.leave.type'

    is_holiday_type = fields.Boolean("Is Holiday Type?", default=False)
