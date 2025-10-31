import time
from datetime import datetime, timedelta

import pytz
from odoo.exceptions import UserError

from odoo import models, fields, _


class EmployeeAbsenceReport(models.TransientModel):
    _name = "employee.absence.report"
    _description = "Employee report for employees who leaves with out information."

    employee_id = fields.Many2one('hr.employee', string="Employee")
    all_employee = fields.Boolean(string="All Employee", default=True)
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date', default=lambda self: fields.Datetime.now())

    def start_date_end_date_range(self, start_date_field, end_date_field):
        delta = end_date_field - start_date_field  # As timedelta
        days = [start_date_field + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_local_time(self, date_to_convert, convert_to_utc=False):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method will give proper format of date and time
        """

        tz = self._context.get('tz', False)
        if not tz:
            tz = self.env.user.tz
            if not tz:
                tz = 'America/Mexico_City'
        start_date = datetime.strptime(date_to_convert.astimezone(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S"),
                                       "%Y-%m-%d %H:%M:%S")
        if convert_to_utc:
            start_date = datetime.strptime(start_date.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
                                           "%Y-%m-%d %H:%M:%S")
        return start_date

    def absence_list_view(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method will saw employees who are absent in the given range date. This method will
                    saw data for all employees or for one employee
        """

        self._cr.execute("delete from absence_report")
        start_date_with_time = self.start_date
        start_date_with_time_after_conversion = self.get_local_time(start_date_with_time)
        start_date_field = start_date_with_time_after_conversion.date()

        end_date_with_time = self.end_date
        end_date_with_time_after_conversion = self.get_local_time(end_date_with_time)
        end_date_field = end_date_with_time_after_conversion.date()

        list_of_dates = self.start_date_end_date_range(start_date_field, end_date_field)
        # domain = [('check_in', '>=', self.start_date), ('check_out', '<=', self.end_date)]
        employees = self.env['hr.employee'].search(['|', ('first_contract_date', '<=', self.start_date), ('first_contract_date', '=', False)])
        domain = ['|', '&', ('check_in', '>=', self.start_date), ('check_out', '<=', self.end_date),
                  ('check_out', '=', False)]
        if not self.all_employee:
            domain.append(('employee_id', '=', self.employee_id.id))
            employees = self.env['hr.employee'].search([('id', '=', self.employee_id.id), '|', ('first_contract_date', '<=', self.start_date), ('first_contract_date', '=', False)])
        record_set = self.env['hr.attendance'].search(domain)
        employees -= record_set.mapped('employee_id')
        hr_leaves_record = False
        employee_list = []
        list_of_all_employee = []
        for employee in employees:
            if employee.id not in employee_list:
                employee_list.append(employee.id)
                hr_leave_domain = []
                if employee.departure_reason_id:
                    list_of_dates = []
                    contract_date = self.env['hr.contract'].search(
                        [('employee_id', '=', employee.id), ('state', 'not in', ['close', 'cancel'])])
                    if contract_date.date_end and end_date_field >= contract_date.date_end:
                        hr_leaves_record = self.env['hr.leave'].search([('employee_id', '=', employee.id)]) \
                            .filtered(lambda
                                          x: x.date_from.month >= self.start_date.month and x.date_to.month <= contract_date.date_end.month)
                        list_of_dates = self.start_date_end_date_range(start_date_field,
                                                                       contract_date.date_end - timedelta(1))
                    elif employee.departure_date and end_date_field >= employee.departure_date:
                        hr_leaves_record = self.env['hr.leave'].search([('employee_id', '=', employee.id)]) \
                            .filtered(lambda
                                          x: x.date_from.month >= self.start_date.month and x.date_to.month <= employee.departure_date.month)
                        list_of_dates = self.start_date_end_date_range(start_date_field,
                                                                       employee.departure_date - timedelta(1))
                    else:
                        list_of_dates = self.start_date_end_date_range(start_date_field, end_date_field)
                else:
                    hr_leaves_record = self.env['hr.leave'].search([('employee_id', '=', employee.id)]).filtered(
                        lambda x: x.date_from.month >= self.start_date.month and x.date_to.month <= self.end_date.month)

                global_leaves = self.env['resource.calendar'].search(
                    [('id', '=', employee.employee_attendance_report_working_hour_id.id)]).global_leave_ids
                converted_date = []
                filter_global_leave = []
                global_leaves_record_set_count = []
                global_leaves_final_record_set_count = []
                employee_id = employee.id

                # Filtered record will get all the leaves
                report_date = record_set.filtered(lambda emp: emp.employee_id.id == employee_id).mapped('check_in')
                report_date.extend(record_set.filtered(lambda emp: emp.employee_id.id == employee_id).mapped('check_out'))
                for day_date in report_date:  # For convert utc to mexico time
                    if not day_date:
                        continue
                    else:
                        dt = self.get_local_time(day_date)
                        converted_date.append(dt)
                filtered_record_set = [curr_date for curr_date in list_of_dates if
                                       curr_date not in [dt.date() for dt in converted_date]]

                # Get all global leaves and store it in list.
                for global_leave in global_leaves:
                    global_leaves_record_set_count.append(global_leave.date_from.date())
                    if global_leave.date_to.date() not in global_leaves_record_set_count:
                        global_leaves_record_set_count.append(global_leave.date_to.date())

                # From the global leaves compare with filtered record set to between in selected range.
                for record in filtered_record_set:
                    if record in global_leaves_record_set_count:
                        filtered_record_set.remove(record)

                # HR record leaves will decrease from the global leaves and total leaves.
                for hr_leave in hr_leaves_record:
                    hr_leave_dates = self.start_date_end_date_range(hr_leave.date_from.date(), hr_leave.date_to.date())
                    global_leaves_final_record_set_count.extend(hr_leave_dates)

                # Remove HR leave from filtered records.
                for global_leave_count in global_leaves_final_record_set_count:
                    if global_leave_count in filtered_record_set:
                        filtered_record_set.remove(global_leave_count)

                for count_global_leave in filtered_record_set:
                    if count_global_leave not in filter_global_leave:
                        filter_global_leave.append(count_global_leave)

                # Employee working hours.
                day_off_in_weeks = [day for day in ['0', '1', '2', '3', '4', '5', '6'] if day not in set(
                    employee.employee_attendance_report_working_hour_id.attendance_ids.mapped('dayofweek'))]
                day_dict = {'0': 'Monday', '1': 'Tuesday', '2': 'Wednesday', '3': 'Thursday', '4': 'Friday',
                            '5': 'Saturday', '6': 'Sunday'}
                date = []
                for absence in day_off_in_weeks:
                    week_day = day_dict[absence]
                    dates = [start_date_field + timedelta(days=x) for x in
                             range((end_date_field - start_date_field).days + 1) if
                             (start_date_field + timedelta(days=x)).weekday() == time.strptime(week_day, '%A').tm_wday]
                    date.extend(dates)

                if not filter_global_leave:
                    continue

                for rec in filter_global_leave:
                    if rec not in date:
                        record_of_employee = {'employee_id': employee.id, 'absence_date': rec}
                        self.env['absence.report'].create(record_of_employee)
                        list_of_all_employee.append(record_of_employee)

        if not list_of_all_employee:
            raise UserError(_('No records found.'))

        view = self.env.ref('setu_employee_attendance_report.absence_report_wizard')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Absence Report'),
            'res_model': 'absence.report',
            'views': [(view.id, 'list')],
            'view_mode': 'list',
            'target': 'current',
        }

    def get_absence_report(self):
        return True


class AbsenceReportTree(models.TransientModel):
    _name = "absence.report"
    _description = "AbsenceReportTree"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    absence_date = fields.Date('Absence Date')
