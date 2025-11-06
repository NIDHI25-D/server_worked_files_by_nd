import json

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def save_attendance(self,attendance_data):
        attendance_data = json.loads(attendance_data)
        for data in attendance_data:
            employee = self.search([('id', '=', data.get('employee_id'))])
            if not employee:
                continue
            modified_attendance = employee.with_user(employee.user_id)._attendance_action_change()
            attendance_type = 'check_in' if employee.attendance_state == 'checked_in' else 'check_out'

            modified_attendance.write({attendance_type: datetime.strptime(data.get('att_date_time'),'%Y-%m-%dT%H:%M:%S.%fZ')})
            if attendance_type == 'check_in':
                modified_attendance.sudo().write({
                    'geo_check_in': '%s'%data.get('location',False),
                })
            if attendance_type == 'check_out':
                modified_attendance.sudo().write({
                    'geo_check_out': '%s' % data.get('location', False),
                })

        return True