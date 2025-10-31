from odoo import models, fields, api


class SetuAttendance(models.Model):
    _name = 'setu.hr.public.holidays'
    _description = 'Public Holidays Management'

    name = fields.Char("Name")
    holiday_start_date = fields.Datetime(string='Holiday date')
    department_ids = fields.Many2many('hr.department', string='Departments')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type')
    note = fields.Text("Note")
    holiday_hours = fields.Float(string='Holiday hours')

    @api.onchange('department_ids')
    def set_department_wise_employees(self):
        """
            Author: jatin@setconsulting
            Date: 13/04/23
            Task: Migration
            Purpose:  Add domain based of employee list based on department ids.
        """
        return {'domain': {'employee_ids': [('department_id', 'in', self.department_ids.ids)]}}
