from lxml import etree

from odoo import _, api, fields, models
from datetime import datetime, date, timedelta
import base64
import pytz
from odoo.exceptions import UserError


class CoreViolation(models.TransientModel):
    _name = "core.violation"
    _description = "Core Violation Report"

    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    all_employee = fields.Boolean(string="All Employee", default=True)
    employee_id = fields.Many2one("hr.employee", string="Employee Name")
    start_time = fields.Char("Start time", default='10:00:00')
    end_time = fields.Char("End time", default='15:00:00')
    file_content = fields.Binary('File Content')

    def date_range(self, start_date_field, end_date_field):
        """
            Authour: nidhi@setconsulting
            Date: 25/05/23
            Task: Migration from v14 to v16
            Purpose: This method is used to create range of dates
        """

        delta = end_date_field - start_date_field  # as timedelta
        days = [start_date_field + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_local_time(self, date_to_convert, convert_to_utc=False):
        """
            Authour: nidhi@setconsulting
            Date: 25/05/23
            Task: Migration from v14 to v16
            Purpose: This method is used to get start time and end time and convert to utc(Coordinated Universal Time)
            Return : start_date
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

    def download_violation_report(self):
        """
            Authour: nidhi@setconsulting
            Date: 25/05/23
            Task: Migration from v14 to v16
            Purpose:-This method is called for button : Create
                    -This method wil generate error if record not found
                    -This method will download the report of employees data related to checked in & out
        """
        start_date_with_time = self.start_date
        start_date_with_time_after_conversion = self.get_local_time(start_date_with_time)
        start_date_field = start_date_with_time_after_conversion.date()

        end_date_with_time = self.end_date
        end_date_with_time_after_conversion = self.get_local_time(end_date_with_time)
        end_date_field = end_date_with_time_after_conversion.date()

        list_of_dates = self.date_range(start_date_field, end_date_field)
        domain = [('check_in', '>=', start_date_field), ('check_in', '<=', end_date_field)]
        if not self.all_employee:
            domain.append(('employee_id', '=', self.employee_id.id))
        record_set = self.env['hr.attendance'].search(domain)
        final_record_set = []
        for date in list_of_dates:
            filtered_record_set = record_set.filtered(lambda x: x.check_in.date() == date)
            employee_list = []
            for record in filtered_record_set:
                if record.employee_id.id not in employee_list:

                    employee_list.append(record.employee_id.id)
                    check_in_records = filtered_record_set.filtered(
                        lambda timesheet: timesheet.employee_id.id == record.employee_id.id)
                    check_in = min(check_in_records.mapped('check_in'))
                    check_out_records = check_in_records.filtered(lambda sheet: sheet.check_out != False)
                    check_out = check_out_records.mapped('check_out')
                    if max(check_in_records) not in check_out_records:
                        check_out = False
                    else:
                        if check_out_records:
                            check_out = max(check_out)

                    start_date_string = date.strftime("%Y-%m-%d")
                    start_time_with_core_start_time = f"{start_date_string}{' '}{self.start_time}"
                    converted_start_datetime = datetime.strptime(start_time_with_core_start_time, '%Y-%m-%d %H:%M:%S')

                    end_date_string = date.strftime("%Y-%m-%d")
                    end_time_with_core_start_time = f"{end_date_string}{' '}{self.end_time}"
                    converted_end_datetime = datetime.strptime(end_time_with_core_start_time, '%Y-%m-%d %H:%M:%S')
                    check_in_converted = self.get_local_time(check_in)
                    check_out_converted = check_out and self.get_local_time(check_out) or False

                    if check_in_converted and check_out_converted:
                        if check_in_converted > converted_start_datetime or check_out_converted < converted_end_datetime or check_out_converted.date() != check_in_converted.date():
                            final_record_set.append(
                                {"employee": record.employee_id.name,
                                 "day": date,
                                 "check_in_violation": check_in_converted,
                                 "check_out_violation": check_out_converted,
                                 "violation_selection": 'both' if check_in_converted > converted_start_datetime and check_out_converted < converted_end_datetime else
                                 'missed' if check_in_converted > converted_start_datetime and check_out_converted.date() != check_in_converted.date() else
                                 'check_in_violation' if check_in_converted > converted_start_datetime else
                                 'check_out_violation' if check_out_converted < converted_end_datetime else
                                 "missed",
                                 "remark_field": f"This user has done process of checkout on {check_out_converted}" if check_out_converted.date() != check_in_converted.date() else " "
                                 })
                    if not check_out_converted and check_in_converted:
                        if not check_out_converted or check_in_converted > converted_start_datetime:
                            final_record_set.append(
                                {"employee": record.employee_id.name,
                                 "day": date,
                                 "check_in_violation": check_in_converted,
                                 "check_out_violation": False,
                                 "violation_selection": 'missed',
                                 "remark_field": "This user has not done process of checkout" if not check_out_converted else " ",
                                 })
        if not final_record_set:
            raise UserError(
                _('No records found.'))

        arg1, arg2 = self.env.ref('core_violation_report.core_violation_report_details').with_context(
            emp_data=final_record_set)._render_qweb_pdf(report_ref='core_violation_report.report_core_violation',
                                                        res_ids=self.ids)
        file_data = base64.encodebytes(arg1)
        self.write({'file_content': file_data})
        return {
            'name': 'Core Violation Report',
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=core.violation&field=file_content&id=%s&filename=core_violation_report.%s' % (
                self.id, arg2),
            'target': 'self',
        }

    def show_violation_report_in_listview(self):
        """
            Authour: nidhi@setconsulting
            Date: 25/05/23
            Task: Migration from v14 to v16
            Purpose:-This method is called for button view data
                    -This method is used to show data in list view :start and end date as well type as per
                      the employee have login.
                    -Type of Violation :
                         1.if employee is checked-in between mentioned hours(wizard) than 'Check in Violation'
                         2.if employee is checked-out between mentioned hours than 'Check out Violation'
                         3.if employee is check in & out between mentioned hours than 'Both'
                         4.if employee is not logout than 'Missed'
                    -Will show error if record not found between the given time
                    -It will also delete list view.
        """

        self._cr.execute("delete from core_violation_tree")

        start_date_with_time = self.start_date
        start_date_with_time_after_conversion = self.get_local_time(start_date_with_time)
        start_date_field = start_date_with_time_after_conversion.date()

        end_date_with_time = self.end_date
        end_date_with_time_after_conversion = self.get_local_time(end_date_with_time)
        end_date_field = end_date_with_time_after_conversion.date()

        list_of_dates = self.date_range(start_date_field, end_date_field)
        domain = [('check_in', '>=', start_date_field), ('check_in', '<=', end_date_field)]
        if not self.all_employee:
            domain.append(('employee_id', '=', self.employee_id.id))

        record_set = self.env['hr.attendance'].search(domain)

        final_record_set = []
        for date in list_of_dates:
            filtered_record_set = record_set.filtered(lambda x: x.check_in.date() == date)
            employee_list = []
            for record in filtered_record_set:
                if record.employee_id.id not in employee_list:

                    employee_list.append(record.employee_id.id)
                    check_in_records = filtered_record_set.filtered(
                        lambda timesheet: timesheet.employee_id.id == record.employee_id.id)
                    check_in = min(check_in_records.mapped('check_in'))
                    check_out_records = check_in_records.filtered(lambda sheet: sheet.check_out != False)
                    check_out = check_out_records.mapped('check_out')
                    if max(check_in_records) not in check_out_records:
                        check_out = False
                    else:
                        if check_out_records:
                            check_out = max(check_out)
                    start_date_string = date.strftime("%Y-%m-%d")
                    start_time_with_core_start_time = f"{start_date_string}{' '}{self.start_time}"
                    converted_start_datetime = datetime.strptime(start_time_with_core_start_time, '%Y-%m-%d %H:%M:%S')

                    end_date_string = date.strftime("%Y-%m-%d")
                    end_time_with_core_start_time = f"{end_date_string}{' '}{self.end_time}"
                    converted_end_datetime = datetime.strptime(end_time_with_core_start_time, '%Y-%m-%d %H:%M:%S')
                    check_in_after_conversion = self.get_local_time(check_in)
                    check_out_after_conversion = check_out and self.get_local_time(check_out) or False
                    if check_in_after_conversion and check_out_after_conversion:
                        if check_in_after_conversion > converted_start_datetime or check_out_after_conversion < converted_end_datetime or check_out_after_conversion.date() != check_in_after_conversion.date():
                            final_record_set.append(
                                {"employee_id": record.employee_id.id, "date": date, "violation_check_in": check_in,
                                 "violation_check_out": check_out,
                                 "remark_field": f"This user has done process of checkout on {check_out_after_conversion}" if check_out_after_conversion.date() != check_in_after_conversion.date() else " ",
                                 "violation_selection": 'both' if check_in_after_conversion > converted_start_datetime and check_out_after_conversion < converted_end_datetime else
                                 'missed' if check_in_after_conversion > converted_start_datetime and check_out_after_conversion.date() != check_in_after_conversion.date() else
                                 'check_in_violation' if check_in_after_conversion > converted_start_datetime else
                                 'check_out_violation' if check_out_after_conversion < converted_end_datetime else
                                 "missed"})
                    if not check_out_after_conversion and check_in_after_conversion:
                        if not check_out_after_conversion or check_in_after_conversion > converted_start_datetime:
                            final_record_set.append(
                                {"employee_id": record.employee_id.id, "date": date, "violation_check_in": check_in,
                                 "violation_check_out": False,
                                 "boolean_check_in": True if check_in_after_conversion > converted_start_datetime else False,
                                 "remark_field": "This user has not done process of checkout" if not check_out_after_conversion else " ",
                                 "violation_selection": 'missed'})

        if not final_record_set:
            raise UserError(
                _('No records found.'))

        for rec in final_record_set:
            self.env['core.violation.tree'].create(rec)

        view = self.env.ref('core_violation_report.core_violation_report_tree')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Core time violation'),
            'res_model': 'core.violation.tree',
            'views': [(view.id, 'tree')],
            'view_mode': 'tree',
            'target': 'current',
        }


class SetuABCSalesAnalysisBIReport(models.TransientModel):
    _name = 'core.violation.tree'
    _description = "Core Violation Tree View"

    employee_id = fields.Many2one("hr.employee", string="Employee Name")
    date = fields.Date(string="Day")
    violation_check_in = fields.Datetime("Check in")
    violation_check_out = fields.Datetime("Check out")
    remark_field = fields.Text(string="Remark")
    boolean_check_in = fields.Boolean("Is boolean check in?")
    boolean_check_out = fields.Boolean("Is boolean out in?")
    violation_selection = fields.Selection([('check_in_violation', 'Check in Violation'),
                                            ("check_out_violation", "Check out violation"),
                                            ("both", "Both"),
                                            ("missed", "Missed")], string='Type of violation')
