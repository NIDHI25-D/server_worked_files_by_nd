import pytz
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    use_for_sales_time_report = fields.Boolean(string="Default work shift ?", copy=False)

    @api.constrains('use_for_sales_time_report')
    def _check_other_shifts(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To raise an error if default work shift is already selected in weekly work shifts calendar view for calculating sales time dashboard report.
        """
        existing = self.search([('use_for_sales_time_report', '=', True), ('id', '!=', self.id)])
        if existing:
            raise ValidationError(_('"%s" is already selected for sales time report, you must deselect it before selecting another shift.' % existing.name))

    def get_standard_work_shift(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To get weekly work shifts calendar of resource which is having default work shift for calculating sales time dashboard report.
        """
        return self.env['resource.calendar'].sudo().search([('use_for_sales_time_report', '=', True)])

    def shift_wise_average_hours(self, shifts):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To get total hours of shifts
        """
        total_hours = 0
        for record in shifts:
            total_hours += (record.hour_to - record.hour_from)
        return total_hours

    def get_shift_wise_hours(self, start_date, end_date):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: (1) To get shift wise hours
                        Example:- if start time is greater than hours from then (minus hours = start time - hours from) is consider in total hours
                                  if end time is less than hours to then (minus hours = start time - hours from) is consider in total hours
        """
        shift = self.get_standard_work_shift()
        try:
            tz_str = shift.tz
            user_tz_object = pytz.timezone(tz_str)
        except:
            user_tz_object = pytz.timezone('America/Mexico_City')

        start_date = datetime.strptime(start_date.astimezone(user_tz_object).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(end_date.astimezone(user_tz_object).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
        if start_date > end_date:
            x = start_date
            start_date = end_date
            end_date = x

        start_time = self.calculate_date_in_float(start_date)
        end_time = self.calculate_date_in_float(end_date)

        leave = shift.global_leave_ids.filtered(lambda x: x.date_from <= start_date <= x.date_to)
        total_shifts = self.total_shifts(shift, start_date, end_date)
        shift_start = not leave and shift.attendance_ids.filtered(
            lambda x: x.dayofweek == str(start_date.weekday()) and (
                        x.hour_from <= start_time and x.hour_to >= start_time)) or False
        shift_end = not leave and shift.attendance_ids.filtered(lambda x: x.dayofweek == str(end_date.weekday()) and (
                    x.hour_from <= end_time and x.hour_to >= end_time)) or False
        total_hours = self.shift_wise_average_hours(total_shifts)
        if shift_start:
            hour_from = sum(shift_start.mapped('hour_from'))
            hour_to = sum(shift_start.mapped('hour_to'))
            minus_hours = start_time - hour_from
            if minus_hours > 0:
                total_hours -= minus_hours
        if shift_end:
            hour_from = sum(shift_end.mapped('hour_from'))
            hour_to = sum(shift_end.mapped('hour_to'))
            minus_hours = hour_to - end_time
            if minus_hours > 0:
                total_hours -= minus_hours
        return round(total_hours, 2) if total_hours > 0 and total_hours is not None else 0

    def total_shifts(self, working_time, start_date, end_date):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: This method consider those shifts in which (start date time and end date time which is come from calculate_date_in_float method) between hour_from and hour_to
        """
        date = start_date
        start_time = self.calculate_date_in_float(start_date)
        end_time = self.calculate_date_in_float(end_date)
        shifts = self.env['resource.calendar.attendance'].sudo()
        total_shifts_obj = self.env['resource.calendar.attendance'].sudo()
        start_date_changed = False
        while True:
            if start_date == date and not start_date_changed:
                date = date
            else:
                date = date + timedelta(days=1)
            leave = working_time.global_leave_ids.filtered(lambda x: x.date_from <= date <= x.date_to)
            if date.date() == end_date.date():
                if start_date.date() == date.date():
                    shift_attendance_records = shifts.search(
                        [('dayofweek', '=', str(date.weekday())), ('calendar_id', '=', working_time.id),
                         '|',('hour_to', '>=', end_time),('hour_to', '>=', start_time)],
                        order='hour_from asc')
                    for record in shift_attendance_records:
                        if (record.hour_from > start_time and record.hour_from > end_time) or (record.hour_to < start_time and record.hour_to < end_time):
                            shift_attendance_records -= record
                else:
                    shift_attendance_records = shifts.search(
                        [('dayofweek', '=', str(date.weekday())), ('calendar_id', '=', working_time.id), ('hour_from', '<=', end_time)],
                        order='hour_from asc')

            else:
                if start_date == date and not start_date_changed:
                    shift_attendance_records = shifts.search(
                        [('dayofweek', '=', str(date.weekday())), ('calendar_id', '=', working_time.id), ('hour_to', '>=', start_time)],
                        order='hour_from asc')
                else:
                    shift_attendance_records = shifts.search(
                        [('dayofweek', '=', str(date.weekday())), ('calendar_id', '=', working_time.id)],
                        order='hour_from asc')
            if start_date == date and not start_date_changed:
                start_date_changed = True
            if not leave and shift_attendance_records:
                total_shifts_obj += shift_attendance_records
            if date.date() == end_date.date():
                break
        return total_shifts_obj

    def calculate_date_in_float(self, date):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To get float value of date for calculating hour which is start time or end time of shift
        """
        date = datetime.strftime(date, '%H:%M')
        time_split = [int(n) for n in date.split(":")]
        current_time_float_value = time_split[0] + time_split[1] / 60.0
        return current_time_float_value
