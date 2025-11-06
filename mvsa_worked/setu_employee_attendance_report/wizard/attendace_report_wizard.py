from odoo import models, fields, api, _,tools
import pytz
from datetime import datetime, date, timedelta
import xlsxwriter
from io import BytesIO
import base64
from ast import literal_eval
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AttendanceReportWizard(models.TransientModel):
    _name = "hr.attendance.reportwizard"
    _description = "Employees actual worked hours against total workings hours report"

    department_ids = fields.Many2many('hr.department', 'hr_department_attendance_wiz_rel', 'department_id', 'wizard_id',
                                      string="Department")
    employee_ids = fields.Many2many('hr.employee', 'hr_emplyee_attendance_wiz_rel', 'employee_id', 'wizard_id',
                                    string="Employee")
    cutover_date = fields.Date(string='Cutover Date')
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    worked_hours = fields.Integer(string="Worked Hours")
    worked_hours_operator = fields.Selection([('more', 'More'), ('less', 'Less'), ('more_or_equal', 'More or equal'),
                                              ('less_or_equal', 'Less or equal')],
                                             string='Worked Hours Operator')
    enable_start_date = fields.Boolean(string="Enable Start Date")

    @api.model
    def default_get(self, fields):
        res = super(AttendanceReportWizard, self).default_get(fields)
        res['cutover_date'] = self.env['ir.config_parameter'].sudo().get_param(
            'setu_employee_attendance_report.cutover_date')
        res['cutover_date'] = datetime.strptime(res['cutover_date'], "%Y-%m-%d").date()
        return res

    @api.onchange('employee_ids')
    def calculate_domain_for_employees(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: Use to calculate domain for user.
        """
        domain = []
        # if self.department_ids:
        # All users
        if self.env.user.has_group(
                'setu_employee_attendance_report.module_setu_employee_employee_attandance_group_all_users'):
            domain = []
            if self.department_ids:
                domain.append(('department_id', 'in', self.department_ids.ids))
        # For manager and sit's subordinate's employee
        elif self.env.user.has_group(
                'setu_employee_attendance_report.module_setu_employee_employee_attandance_group_manager'):
            ids = []
            ids.append(self.env.user.employee_id.id)
            ids.extend(self.env.user.employee_id.child_ids.ids)
            domain.append(('id', 'in', ids))
        elif self.env.user.has_group(
                'setu_employee_attendance_report.module_setu_employee_employee_attandance_group_user'):
            domain.append(('id', '=', self.env.user.employee_id.id))
        else:
            domain.append(('id', '=', False))
        # domain = [('id','=',670)]

        return {'domain': {'employee_ids': domain}}

    @api.onchange('department_ids')
    def set_department_wise_employees(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: In this method domain is to used give employees of particular departmnent
        """

        domain = []
        if self.department_ids:
            domain = [('department_id', 'in', self.department_ids.ids)]

        return {'domain': {'employee_ids': domain}}

    def attendance_report(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method is used to create a report of the employees by taking data from different methods.
        """

        attendance_data = self.get_attendance_analysis_report_data()
        for attendance_data_value in attendance_data:
            attendance_data_value['wizard_id'] = self.id
            at = self.env['hr.attendance.bi.report'].create(attendance_data_value)
            at.with_context(not_from_cron = True)._get_leaves_data()
            at.compute_holiday_hours()
            at._get_attendance()
            at.compute_over_time_hours()
            at.compute_total_hours()

        tree_view_id = self.env.ref('setu_employee_attendance_report.hr_attendance_report_tree_view').id
        form_view_id = self.env.ref('setu_employee_attendance_report.hr_attendance_bi_report_form').id
        report_display_views = [(tree_view_id, 'list'), (form_view_id, 'form')]
        viewmode = "list,form"

        return {
            'name': _('Employee attendance report'),
            # 'name': _('Employee attendance report From %s to %s') % (self.start_date, self.end_date),
            'domain': [('wizard_id', '=', self.id)],
            'res_model': 'hr.attendance.bi.report',
            'view_mode': viewmode,
            'type': 'ir.actions.act_window',
            'views': report_display_views,
            'help': """
                        <p class="o_view_nocontent_smiling_face">
                            No data found.
                        </p>
                    """,
        }

    def get_attendance_analysis_report_data(self):
        """
        :return:
        """

        end_date = self.end_date
        department_ids = self.department_ids and set(self.department_ids.ids) or {}
        for employee in self.employee_ids:
            if not employee.employee_attendance_report_working_hour_id:
                raise ValidationError(_('Please add working hours for employee %s' % (employee.name)))
        employee_ids = self.employee_ids and set(self.employee_ids.ids) or {}

        if self.enable_start_date:
            start_date = self.start_date
            query = """Select * from get_employee_attendance_data('%s','%s','%s','%s','%s','%s')
                        """ % (department_ids, employee_ids, start_date, end_date, self.worked_hours, self.worked_hours_operator)
        else:
            query = """Select * from get_employee_attendance_data_without_cron('%s','%s','%s','%s','%s')
                """ % (department_ids, employee_ids, end_date, self.worked_hours, self.worked_hours_operator)
        self._cr.execute(query)
        return self._cr.dictfetchall()


class AttendenceReport(models.TransientModel):
    _name = "hr.attendance.bi.report"
    _description = "Employees actual worked hours analysis report"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    resource_calendar_id = fields.Many2one("resource.calendar", "Working hours",
                                           related='employee_id.employee_attendance_report_working_hour_id')
    department_id = fields.Many2one('hr.department', string='Deparment')
    expected_working_hours = fields.Float(string='Expected working hours')
    holiday_hours = fields.Float(string='Holiday hours', compute="compute_holiday_hours", store=True)
    absence_hours = fields.Float(string='Absences', compute="compute_holiday_hours", store=True)
    real_worked_hours = fields.Float(string='Real worked hours', compute='_get_attendance', store=True)
    total_hours = fields.Float(string='Total', compute="compute_total_hours", store=True)
    difference = fields.Float(string='Difference', compute="compute_total_hours", store=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance', compute='_get_attendance')
    leave_ids = fields.Many2many('hr.leave', string='Leaves', compute='_get_leaves_data')
    # holiday_ids = fields.Many2many('hr.holiday', string='Holidays', compute='')
    wizard_id = fields.Many2one('hr.attendance.reportwizard', string='Wizard ID')
    over_time_hours = fields.Float(string="Overtime", compute='compute_over_time_hours', store=True)

    def get_local_time(self, date_to_convert, convert_to_utc=False):
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

    def _get_attendance(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method will sum worked hours of employee to get their attendance
        """
        _logger.debug("Compute _get_attendance method start")
        for report in self:
            domain = [('employee_id', '=', report.employee_id.id), ('check_in', '>=', report.wizard_id.start_date),
                      ('check_in', '<=', report.wizard_id.end_date)]
            attendance_ids = self.env['hr.attendance'].search(domain)
            report.real_worked_hours = sum(attendance_ids.mapped('worked_hours'))
            report.attendance_ids = [(6, 0, attendance_ids.ids)]
        _logger.debug("Compute _get_attendance method end")

    def _get_leaves_data(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose:  This method will give data of leaves
        """
        _logger.debug("Compute _get_leaves_data method start")
        for leave in self:
            if self._context.get('not_from_cron') and not leave.wizard_id.enable_start_date:
                if leave.employee_id.incom_date >= leave.wizard_id.cutover_date:
                    if  leave.wizard_id.end_date >= leave.employee_id.incom_date :
                            leave.wizard_id.start_date = leave.employee_id.incom_date
                    else :
                        if self.env.user.lang == 'es_MX':
                            raise ValidationError(
                                _('La fecha final es inferior a la fecha de ingreso (%s) del empleado %s, por favor modifíquelo' % (
                                leave.employee_id.incom_date, leave.employee_id.name)))
                        raise ValidationError(_('End Date is less than income date (%s) of employee %s, kindly modify end date' %(leave.employee_id.incom_date,leave.employee_id.name)))
                else:
                    if leave.employee_id.incom_date <= leave.wizard_id.cutover_date :
                        if leave.wizard_id.end_date >= leave.wizard_id.cutover_date:
                            leave.wizard_id.start_date = leave.wizard_id.cutover_date
                        else :
                            if self.env.user.lang == 'es_MX' :
                                raise ValidationError(
                                    _('Por favor, seleccione la fecha final correcta porque la fecha de inicio es inferior a la fecha de corte (%s) del empleado: %s' % (
                                    leave.wizard_id.cutover_date, leave.employee_id.name)))
                            raise ValidationError(_('Kindly add proper End Date because start date is less than Cutover date (%s) of employee : %s' %(leave.wizard_id.cutover_date,leave.employee_id.name)))

            domain = [('employee_id', '=', leave.employee_id.id), '|', '&',
                      ('date_from', '>=', leave.wizard_id.start_date), ('date_from', '<=', leave.wizard_id.end_date),
                      '&', ('date_to', '>=', leave.wizard_id.start_date), ('date_to', '<=', leave.wizard_id.end_date),
                      ('state', '=', 'validate')]
            # below domain -- if wizard date is between leave's from and to date [UR]
            leave_ids = self.env['hr.leave'].search(domain).ids
            if not leave_ids:
                domain = [('employee_id', '=', leave.employee_id.id), ('date_from', '<=', leave.wizard_id.start_date),
                          ('date_to', '>=', leave.wizard_id.end_date), ('state', '=', 'validate')]
                leave_ids = self.env['hr.leave'].search(domain).ids

            leave.leave_ids = [(6, 0, leave_ids)]
        _logger.debug("Compute _get_leaves_data method end")

    def compute_holiday_hours(self):
        """
          Author: jatin.babariya@setconsulting.com
          Date: 02/04/25
          Task: Migration from V16 to V18
          Purpose:  This method will give sum of total holiday hours from global leaves mentioned in overtime
                    request module.
        """
        _logger.debug("Compute compute_holiday_hours start")
        for report in self:
            working_hours = report.resource_calendar_id
            holiday_hr = 0.0
            absense_hours_report = 0.0
            global_leaves = working_hours.global_leave_ids.filtered(lambda
                                                                        l: l.date_from.date() >= report.wizard_id.start_date and l.date_from.date()<=report.wizard_id.end_date)
            for same in global_leaves:
                leave_starting_date = datetime.strptime(
                    same.date_from.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                    "%Y-%m-%d %H:%M:%S")
                leave_ending_date = datetime.strptime(
                    same.date_to.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                    "%Y-%m-%d %H:%M:%S")
                leave_starting_hour = leave_starting_date.hour
                leave_ending_hour = leave_ending_date.hour
                start_weekday = leave_starting_date.weekday()
                end_weekday = leave_ending_date.weekday()
                shifts = []
                if leave_starting_date.weekday() != leave_ending_date.weekday():
                    for index in range(start_weekday,end_weekday+1,1):
                        if index == start_weekday or index != end_weekday:
                            shifts.extend(working_hours.attendance_ids.filtered(
                                lambda a: int(a.dayofweek) == index and a.hour_from and leave_starting_hour < 23))
                        else:
                            shifts.extend(working_hours.attendance_ids.filtered(
                                lambda a: int(a.dayofweek) == index and a.hour_from < leave_ending_date.hour))

                else:
                    shifts = working_hours.attendance_ids.filtered(
                        lambda a: int(a.dayofweek) == leave_starting_date.weekday())
                for i in shifts:
                    if leave_starting_hour <= i.hour_from and leave_ending_hour >= i.hour_to or (leave_starting_hour >= i.hour_from and leave_ending_hour >= i.hour_to and leave_starting_hour >= leave_ending_hour):
                        holiday_hr += (i.hour_to - i.hour_from)
                        continue
                    if (
                            leave_starting_hour >= i.hour_from and leave_starting_hour <= i.hour_to) and leave_ending_hour >= i.hour_to or (leave_starting_hour > i.hour_from and leave_starting_hour <= i.hour_to):
                        holiday_hr += (i.hour_to - leave_starting_hour)
                        continue
                    if (leave_starting_hour > i.hour_from and leave_starting_hour < i.hour_to) and (
                            leave_ending_hour > i.hour_from and leave_ending_hour < i.hour_to):
                        holiday_hr += (leave_ending_hour - leave_starting_hour)
                        continue
                    if leave_starting_hour <= i.hour_from and (
                            leave_ending_hour > i.hour_from and leave_ending_hour < i.hour_to):
                        holiday_hr += (leave_ending_hour - i.hour_from)
                        continue
                    if leave_starting_hour <= i.hour_from and leave_ending_hour < i.hour_to:
                        holiday_hr += (i.hour_to - i.hour_from)
                        continue
            for leave in report.leave_ids:
                # include only wizard date leave not all leave[UR]
                converted_start_date = False
                converted_end_date = False
                if report.wizard_id.start_date > leave.date_from.date():
                    get_local_date = report.get_local_time(leave.date_from)
                    converted_start_date = datetime.combine(report.wizard_id.start_date, get_local_date.time())
                else:
                    converted_start_date = datetime.strptime(
                        leave.date_from.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                        "%Y-%m-%d %H:%M:%S")

                if report.wizard_id.end_date < leave.date_to.date():
                    get_local_date = report.get_local_time(leave.date_to)
                    converted_end_date = datetime.combine(report.wizard_id.end_date, get_local_date.time())
                else:
                    converted_end_date = datetime.strptime(
                        leave.date_to.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                        "%Y-%m-%d %H:%M:%S")

                sdate = converted_start_date.date()  # start date
                edate = converted_end_date.date()  # end date
                delta = edate - sdate  # as timedelta
                working_days_shifts = working_hours.attendance_ids.mapped('dayofweek')
                weekdays_of_leaves = []
                for i in range(delta.days + 1):
                    day = sdate + timedelta(days=i)
                    if str(day.weekday()) in working_days_shifts:
                        weekdays_of_leaves.append(day.weekday())
                if leave.holiday_status_id.is_holiday_type:
                    holiday_hours_req = leave.number_of_days_display * report.resource_calendar_id.hours_per_day
                    holiday_hr += holiday_hours_req
                else:
                    if converted_start_date.date() == converted_end_date.date():
                        shifts_of_leaves = working_hours.attendance_ids.filtered(lambda a: int(
                            a.dayofweek) == converted_start_date.weekday())
                    else:
                        # leave_shifts = working_hours.attendance_ids.filtered(lambda a: int(a.dayofweek) >=converted_start_date.weekday() and int(a.dayofweek) <= converted_end_date.weekday())
                        leave_shifts = []
                        for ls in weekdays_of_leaves:
                            # leave_shifts.append(working_hours.attendance_ids.filtered(lambda a: a.dayofweek == str(ls)))
                            # if report.get_local_time(leave.date_to).date.hour ==
                            leave_shifts += working_hours.attendance_ids.filtered(
                                lambda a: a.dayofweek == str(ls)).ids
                        # leave_shifts = working_hours.attendance_ids.filtered(lambda a: int(a.dayofweek) in shift_for_leaves)
                        shifts_of_leaves = self.env['resource.calendar.attendance'].browse(leave_shifts)

                    start_hour = converted_start_date.hour
                    end_hour = converted_end_date.hour
                    for shift in shifts_of_leaves:
                        if int(shift.dayofweek) == converted_start_date.weekday() or int(
                                shift.dayofweek) == converted_end_date.weekday():
                            if int(shift.dayofweek) == converted_end_date.weekday() and converted_start_date.date() != converted_end_date.date():
                                start_hour = 0
                            elif converted_start_date.date() != converted_end_date.date():
                                end_hour = 23
                            if (start_hour > shift.hour_from and start_hour < shift.hour_to) and (
                                    end_hour > shift.hour_from and end_hour < shift.hour_to):
                                absense_hours_req = (end_hour - start_hour)
                                absense_hours_report += absense_hours_req
                                continue
                            if (
                                    start_hour > shift.hour_from and start_hour < shift.hour_to) and end_hour >= shift.hour_to:
                                absense_hours_req = (shift.hour_to - start_hour)
                                absense_hours_report += absense_hours_req
                                continue
                            if start_hour <= shift.hour_from and (
                                    end_hour > shift.hour_from and end_hour < shift.hour_to):
                                absense_hours_req = (shift.hour_to - shift.hour_from)
                                absense_hours_report += absense_hours_req
                                continue
                            if (start_hour <= shift.hour_from and end_hour >= shift.hour_to):
                                absense_hours_req = (shift.hour_to - shift.hour_from)
                                absense_hours_report += absense_hours_req
                        else:
                            absense_hours_req = (shift.hour_to - shift.hour_from)
                            absense_hours_report += absense_hours_req

            report.holiday_hours = holiday_hr
            report.absence_hours = absense_hours_report
        _logger.debug("Compute compute_holiday_hours end")

    def compute_total_hours(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method will give total hours of an employee
        """

        for report in self:
            total_hr = report.holiday_hours + report.absence_hours + report.real_worked_hours + report.over_time_hours
            diff_hr = total_hr - report.expected_working_hours
            report.total_hours = total_hr
            report.difference = diff_hr

    def compute_over_time_hours(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method will give over time hours of an employee
        """
        _logger.debug("Compute compute_over_time_hours method start")
        for report in self:
            working_hours = report.resource_calendar_id
            domain = [('employee_id', '=', report.employee_id.id), '|', '&',
                      ('date_from', '>=', report.wizard_id.start_date), ('date_from', '<=', report.wizard_id.end_date),
                      '&', ('date_to', '>=', report.wizard_id.start_date), ('date_to', '<=', report.wizard_id.end_date),
                      ('state', '=', 'approved')]
            over_time = report.env['hr.overtime'].search(domain)
            total_hour = 0
            for ot in over_time:
                ot_converted_start_date = datetime.strptime(
                    ot.date_from.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                    "%Y-%m-%d %H:%M:%S")
                ot_converted_end_date = datetime.strptime(
                    ot.date_to.astimezone(pytz.timezone(working_hours.tz)).strftime("%Y-%m-%d %H:%M:%S"),
                    "%Y-%m-%d %H:%M:%S")
                if ot.duration_type == 'hours':
                    if ot.overtime_type_id.overtime_type == 'add':
                        total_hour += ot.days_no_tmp
                    else:
                        total_hour -= ot.days_no_tmp
                else:
                    leave_shifts = working_hours.attendance_ids.filtered(
                        lambda a: int(a.dayofweek) >= ot_converted_start_date.weekday() and int(
                            a.dayofweek) <= ot_converted_end_date.weekday())
                    for shift in leave_shifts:
                        st_hour = ot_converted_start_date.hour
                        en_hour = ot_converted_end_date.hour
                        if int(shift.dayofweek) == ot_converted_start_date.weekday() or int(
                                shift.dayofweek) == ot_converted_end_date.weekday():
                            if int(shift.dayofweek) == ot_converted_end_date.weekday() and ot_converted_start_date.date() != ot_converted_end_date.date():
                                st_hour = 0
                            elif ot_converted_start_date.date() != ot_converted_end_date.date():
                                en_hour = 23
                            if (st_hour > shift.hour_from and st_hour < shift.hour_to) and (
                                    en_hour > shift.hour_from and en_hour < shift.hour_to):
                                if ot.overtime_type_id.overtime_type == 'add':
                                    total_hour += (en_hour - st_hour)
                                else:
                                    total_hour -= (en_hour - st_hour)
                                continue
                            if (st_hour > shift.hour_from and st_hour < shift.hour_to) and en_hour >= shift.hour_to:
                                if ot.overtime_type_id.overtime_type == 'add':
                                    total_hour += (shift.hour_to - st_hour)
                                else:
                                    total_hour -= (shift.hour_to - st_hour)
                                continue
                            if st_hour <= shift.hour_from and (en_hour > shift.hour_from and en_hour < shift.hour_to):
                                if ot.overtime_type_id.overtime_type == 'add':
                                    total_hour += (en_hour - shift.hour_from)
                                else:
                                    total_hour -= (en_hour - shift.hour_from)
                                continue
                            if (st_hour <= shift.hour_from and en_hour >= shift.hour_to):
                                if ot.overtime_type_id.overtime_type == 'add':
                                    total_hour += (shift.hour_to - shift.hour_from)
                                else:
                                    total_hour -= (shift.hour_to - shift.hour_from)
                        else:
                            if ot.overtime_type_id.overtime_type == 'add':
                                total_hour += (shift.hour_to - shift.hour_from)
                            else:
                                total_hour -= (shift.hour_to - shift.hour_from)
            report.over_time_hours = total_hour
        _logger.debug("Compute compute_over_time_hours method end")

    def get_weekly_attendance_report(self, is_daily_cron=False):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: This method is called when cron is active, it will create a xls file of weekly data and send via mail
        """

        today = date.today()
        att_report_obj = self.env['hr.attendance.bi.report']
        wiz_obj = self.env['hr.attendance.reportwizard']
        if is_daily_cron:
            start_date = today - timedelta(days=1)
            end_date = start_date
            hr_manager = self.env['ir.config_parameter'].sudo().get_param(
                'setu_employee_attendance_report.hr_manager_id') or False
            employees = self.env['hr.employee'].browse(int(hr_manager)) if hr_manager else []
        else:
            idx = (today.weekday() + 1) % 7
            end_date = today - timedelta(idx)
            start_date = today - timedelta(7 + idx)
            employees = self.env['hr.employee'].search([])
        wizard = wiz_obj.create({'start_date': start_date, 'end_date': end_date})
        # TASK : https://app.clickup.com/t/86drq7uuw {Change in attendance report and add field in employee.}
        employees_without_working_hour = employees.filtered(lambda emp: not emp.employee_attendance_report_working_hour_id)
        if employees_without_working_hour:
            names = '\n'.join(employees_without_working_hour.mapped('name'))
            raise ValidationError(_('Please add working hours for the following employees:\n%s' % names))
        for emp in employees:
            self._cr.execute('TRUNCATE TABLE hr_attendance_bi_report')
            self._cr.commit()
            ch_ids = {} if is_daily_cron else set(emp.child_ids.ids)
            if start_date.weekday() == 6:
                is_daily_cron = False
            if ch_ids or is_daily_cron:
                attendance_data = self.get_attendance_report_data(employee_ids=ch_ids, start_date=start_date,
                                                                  end_date=end_date)
                for attendance_data_value in attendance_data:
                    attendance_data_value['wizard_id'] = wizard.id
                    at = att_report_obj.create(attendance_data_value)
                    at._get_leaves_data()
                    at.compute_holiday_hours()
                    at._get_attendance()
                    at.compute_over_time_hours()
                    at.compute_total_hours()
                    at._flush()

                self._cr.execute("""SELECT he.name as Employee,
                                            hd.name as Department,
                                            atr.expected_working_hours as Expected_Working_Hours,
                                            atr.holiday_hours as Holiday_Hours,
                                            atr.absence_hours as Absence_Hours,
                                            atr.real_worked_hours as Real_Worked_Hours,
                                            atr.over_time_hours as Overtime,
                                            atr.total_hours as Total_Hours,
                                            atr.difference as Difference  
                                                FROM hr_attendance_bi_report atr
                                                LEFT join hr_employee he on atr.employee_id = he.id
                                                LEFT join hr_department hd on hd.id = atr.department_id
                                                """)
                attendance_report = self._cr.dictfetchall()
                file_pointer = BytesIO()
                workbook = xlsxwriter.Workbook(file_pointer)
                worksheet = workbook.add_worksheet()
                header = list(attendance_report[0].keys())
                cell_format = workbook.add_format({'bold': True})
                if is_daily_cron:
                    worksheet.write(0, 3, f'Attendance worked Hours report of {start_date}', cell_format)
                else:
                    worksheet.write(0, 3, f'Attendance worked Hours report from {start_date} To {end_date}',
                                    cell_format)
                row = 1
                col = 0
                for cost in header:
                    worksheet.write(row, col, cost, cell_format)
                    worksheet.set_column(col, col, 20)
                    col += 1
                row = 2

                for i in attendance_report:
                    col = 0
                    for val in i.values():
                        val = str(val)
                        worksheet.write(row, col, val)
                        col += 1
                    row += 1

                workbook.close()
                file_pointer.seek(0)
                file_data = base64.encodebytes(file_pointer.read())
                self.write({'datas': file_data})
                file_pointer.close()

                att = self.env['ir.attachment'].create({
                    'name': f"Attendance report from {start_date} To {end_date}.xls",
                    'datas': file_data,
                    'res_model': 'import.csv.record.log',
                    'res_id': self.id,
                    'type': 'binary',
                })
                vals = {'email': emp.work_email, 'name': emp.name, 'report': 'daily' if is_daily_cron else 'weekly'}
                template_id = self.env.ref(
                    'setu_employee_attendance_report.email_template_to_send_attendance_data_to_manager').id
                template = self.env['mail.template'].browse(template_id)
                template.attachment_ids = [(6, 0, att.ids)]
                template.with_context(vals).send_mail(self.env.user.id, force_send=True)

    def get_attendance_report_data(self, employee_ids, start_date, end_date):
        department_ids = {}
        worked_hours = 0
        worked_hours_operator = False
        start_date = start_date
        end_date = end_date
        query = """select * from get_employee_attendance_data('%s','%s','%s','%s','%s','%s')""" % (department_ids, employee_ids, start_date, end_date, worked_hours, worked_hours_operator)

        self._cr.execute(query)
        return self._cr.dictfetchall()

    def get_daily_attendance_report(self):
        self.get_weekly_attendance_report(is_daily_cron=True)

    def get_weekly_attendance_by_employee_report(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose: Use when call this cron Weekly Attendance report for employee cron.
        """
        today = date.today()
        att_report_obj = self.env['hr.attendance.bi.report']
        wiz_obj = self.env['hr.attendance.reportwizard']
        idx = (today.weekday() + 1) % 7
        end_date = today - timedelta(idx)
        start_date = today - timedelta(7 + idx)
        employees_to_exclude_from_mail = self.env["ir.config_parameter"].sudo().get_param('setu_employee_attendance_report.hr_employee_ids', '[]')
        employees_list_to_exclude = literal_eval(employees_to_exclude_from_mail)
        employees = self.env['hr.employee'].search([])
        if employees_list_to_exclude:
            employees = employees.filtered(lambda exculde:exculde.id not in employees_list_to_exclude)
        wizard = wiz_obj.create({'start_date': start_date, 'end_date': end_date})
        for emp in employees:
            if not emp.employee_attendance_report_working_hour_id:
                raise ValidationError(_('Please add working hours for employee %s' % (emp.name)))
            self._cr.execute('TRUNCATE TABLE hr_attendance_bi_report')
            self._cr.commit()
            emp_id = set([emp.id])
            attendance_data = self.get_attendance_report_data(employee_ids=emp_id, start_date=start_date,
                                                              end_date=end_date)
            for attendance_data_value in attendance_data:
                attendance_data_value['wizard_id'] = wizard.id
                at = att_report_obj.create(attendance_data_value)
                at._get_leaves_data()
                at.compute_holiday_hours()
                at._get_attendance()
                at.compute_over_time_hours()
                at.compute_total_hours()
                at._flush()

            self._cr.execute("""SELECT he.name as Employee,
                                                hd.name as Department,
                                                atr.expected_working_hours as Expected_Working_Hours,
                                                atr.holiday_hours as Holiday_Hours,
                                                atr.absence_hours as Absence_Hours,
                                                atr.real_worked_hours as Real_Worked_Hours,
                                                atr.over_time_hours as Overtime,
                                                atr.total_hours as Total_Hours,
                                                atr.difference as Difference  
                                                    FROM hr_attendance_bi_report atr
                                                    LEFT join hr_employee he on atr.employee_id = he.id
                                                    LEFT join hr_department hd on hd.id = atr.department_id
                                                    """)
            attendance_report = self._cr.dictfetchall()
            attendance_report[0].update({'expected_working_hours': tools.format_duration(float(attendance_report[0].get('expected_working_hours'))), 'holiday_hours': tools.format_duration(float(attendance_report[0].get('holiday_hours'))), 'absence_hours':tools.format_duration(float(attendance_report[0].get('absence_hours'))), 'real_worked_hours': tools.format_duration(float(attendance_report[0].get('real_worked_hours'))), 'overtime': tools.format_duration(float(attendance_report[0].get('overtime'))), 'total_hours': tools.format_duration(float(attendance_report[0].get('total_hours'))), 'difference': tools.format_duration(float(attendance_report[0].get('difference')))})
            file_pointer = BytesIO()
            workbook = xlsxwriter.Workbook(file_pointer)
            worksheet = workbook.add_worksheet()
            header = list(attendance_report[0].keys())
            cell_format = workbook.add_format({'bold': True})

            worksheet.write(0, 3, f'Attendance worked Hours report from {start_date} To {end_date}',
                                cell_format)
            row = 1
            col = 0
            for cost in header:
                worksheet.write(row, col, cost, cell_format)
                worksheet.set_column(col, col, 20)
                col += 1
            row = 2

            for i in attendance_report:
                col = 0
                for val in i.values():
                    val = str(val)
                    worksheet.write(row, col, val)
                    col += 1
                row += 1

            workbook.close()
            file_pointer.seek(0)
            file_data = base64.encodebytes(file_pointer.read())
            self.write({'datas': file_data})
            file_pointer.close()

            att = self.env['ir.attachment'].create({
                'name': f"Attendance report from {start_date} To {end_date}.xls",
                'datas': file_data,
                'res_model': 'import.csv.record.log',
                'res_id': self.id,
                'type': 'binary',
            })
            lang = emp.user_id.partner_id.lang
            vals = {'email': emp.work_email, 'name': emp.name, 'report': 'weekly','lang':lang}
            template_id = self.env.ref(
                'setu_employee_attendance_report.email_template_to_send_attendance_data_to_employee').id
            template = self.env['mail.template'].browse(template_id)
            template.attachment_ids = [(6, 0, att.ids)]
            template.with_context(vals).send_mail(self.env.user.id, force_send=True)
