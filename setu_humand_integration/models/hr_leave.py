# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
import requests
from datetime import datetime, timedelta
from pytz import timezone

_logger = logging.getLogger('Setu_Humand_Integration')


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    humand_time_off_id = fields.Integer(string="Humand Time Off Id")

    def create_time_off_requests_from_humand_cron(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To create Auto Time-Off requests from humand api though the scheduled action.
        """
        humand_access_token = self.env.company.humand_access_token or ''
        days = int(
            self.env['ir.config_parameter'].get_param('setu_humand_integration.days_to_get_time_off_requests')) or 0
        if humand_access_token and days:
            request_date_from = datetime.now() - timedelta(days=days)
            url = f"https://api-prod.humand.co/public/api/v1/time-off/requests?page=1&limit=500&states=APPROVED&fromDate={request_date_from.strftime('%Y-%m-%d')}"
            headers = {
                'Authorization': humand_access_token,
                'accept': 'application/json'
            }
            try:
                response = requests.request("GET", url, headers=headers, data={})
            except:
                if response.status_code == 400:
                    _logger.info('The provided data is invalid')
                elif response.status_code == 401:
                    _logger.info('Invalid credentials')
                elif response.status_code == 403:
                    _logger.info(f'Cannot access this resource')
                elif response.status_code == 500:
                    _logger.info('An unexpected error has occurred')
                else:
                    _logger.info(f"Can't Adapt Resource Because {response.status_code}.")
            if response.status_code in [200, 201]:
                response_dict = response.json()
                records = sorted(response_dict.get('items', {}),
                                 key=lambda x: datetime.strptime(x.get('from', {}).get('date'), '%Y-%m-%d'))
                if records:
                    for record in records:
                        humand_leave_id = self.search([('humand_time_off_id', '=', record.get('id'))])
                        if not humand_leave_id:
                            work_email = record.get('issuer').get('employeeInternalId', '')
                            policy_type = record.get('policyType').get('id', False)
                            date_from = record.get('from').get('date', False)
                            date_to = record.get('to').get('date', False)
                            name = record.get('description', '')
                            humand_time_off_id = record.get('id', False)
                            if all([work_email, date_from, date_to, humand_time_off_id, policy_type]):
                                employee_id = self.env['hr.employee'].search([('work_email', '=', work_email)], limit=1)
                                policy_type_id = self.env['hr.leave.type'].search(
                                    [('humand_allocation_id', '=', policy_type)],
                                    limit=1)
                                if employee_id and policy_type_id:
                                    from_date = datetime.strptime(date_from, "%Y-%m-%d").replace(hour=0, minute=0,
                                                                                                 second=0)
                                    to_date = datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59,
                                                                                             second=59)
                                    # made below changes as per the task - https://app.clickup.com/t/86dx40rqz
                                    attendance_from = attendance_to = False
                                    total_hours = standard_day_hours = 0.0
                                    tz_name = self.env.context.get('tz') or 'UTC'
                                    tz = timezone(tz_name)
                                    calendar_id = employee_id.resource_calendar_id
                                    resource_id = employee_id.resource_id
                                    from_date = tz.localize(from_date)
                                    to_date = tz.localize(to_date)
                                    if calendar_id and resource_id:
                                        intervals_map = calendar_id._attendance_intervals_batch(
                                            from_date,
                                            to_date,
                                            resources=[resource_id],
                                            tz=tz
                                        )
                                        work_intervals = intervals_map.get(resource_id.id)
                                        interval_list = list(work_intervals) if work_intervals else []

                                        if interval_list:
                                            attendance_from = interval_list[0][0]
                                            attendance_to = interval_list[-1][1]
                                            total_hours = sum(
                                                (stop - start).total_seconds() / 3600.0
                                                for start, stop, _ in interval_list
                                            )
                                            standard_day_hours = calendar_id.hours_per_day


                                    from_date = self._to_utc(from_date, attendance_from.hour, employee_id) if attendance_from else from_date
                                    to_date = self._to_utc(to_date, attendance_to.hour, employee_id) if attendance_to else to_date
                                    remaining_days_disct = policy_type_id.get_allocation_data(employee_id, from_date.date()) or {}
                                    employee_data = remaining_days_disct.get(employee_id)
                                    remaining_days = 0
                                    if employee_data and isinstance(employee_data, list) and len(employee_data) > 0:
                                        remaining_days = int(employee_data[0][1].get('remaining_leaves') or 0)
                                    # remaining_days = int(remaining_days_disct.get(employee_id)[0][1].get('remaining_leaves') or 0)

                                    requested_days = int(total_hours / standard_day_hours) if standard_day_hours != 0.0 else 0.0

                                    # self._get_durations()[leave.id]
                                    if requested_days > remaining_days:
                                        if not remaining_days:
                                            _logger.info(
                                                f'There Are No Remaining Days Of {policy_type_id.name} For Employee {employee_id.name}.')
                                            continue
                                        difference_days = requested_days - remaining_days
                                        _logger.info(
                                            f'Reducing Days Because Remaining Days are {remaining_days} For Employee {employee_id.name}.')
                                        to_date -= timedelta(days=difference_days)
                                    vals = {
                                        'name': name,
                                        'holiday_status_id': policy_type_id.id,
                                        'employee_id': employee_id.id,
                                        'request_date_from': from_date,
                                        'request_date_to': to_date,
                                        'date_from': from_date,
                                        'date_to': to_date,
                                        'humand_time_off_id': humand_time_off_id,
                                        'state': 'confirm'
                                    }
                                    if vals:
                                        leave_id = self.create(vals)
                                        if requested_days > remaining_days:
                                            leave_id.message_post(body=_(
                                                f"The Time-Off is created with less amount of days because remaining days are {remaining_days} and requested are {requested_days}."))
                                            _logger.info(
                                                f"The Time-Off is created with less amount of days because remaining days are {remaining_days} and requested are {requested_days}.")
                                        leave_id.action_validate()
                                else:
                                    if not employee_id:
                                        _logger.info(
                                            f'There are no matching employee for this Employee Internal Id {work_email}.')
                                    elif not policy_type_id:
                                        _logger.info(f'There are no matching time-off types for this Id {policy_type}.')
                            if not all([work_email, date_from, date_to, humand_time_off_id, policy_type]):
                                _logger.info(
                                    "Can't Create Time-Off Because There Is Something missing In Response Information.")
                else:
                    _logger.info(
                        "There Are No Request To Create Time-Off.")
