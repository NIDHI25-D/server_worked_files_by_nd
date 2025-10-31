from odoo import models,fields



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_attendance_report_working_hour_id = fields.Many2one('resource.calendar',string="Attendance report working hours.")
