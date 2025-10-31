# -*- coding: utf-8 -*-

from dateutil import relativedelta
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.addons.resource.models.utils import HOURS_PER_DAY
import logging

_logger = logging.getLogger(__name__)


class HrOverTime(models.Model):
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.onchange('days_no_tmp')
    def _onchange_days_no_tmp(self):
        self.days_no = self.days_no_tmp

    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   store=True)
    current_user_boolean = fields.Boolean()
    project_id = fields.Many2one('project.project', string="Project")
    project_manager_id = fields.Many2one('res.users', string="Project Manager")
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date to')
    days_no_tmp = fields.Float('Hours', compute="_get_days", store=True)
    days_no = fields.Float('No. of Days', store=True)
    desc = fields.Text('Description')
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft")
    cancel_reason = fields.Text('Refuse Reason')
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID")
    attchd_copy = fields.Binary('Attach A File')
    attchd_copy_name = fields.Char('File Name')
    type = fields.Selection([('cash', 'Cash'), ('leave', 'leave')], default="leave", required=True, string="Type")
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    overtime_type_id = fields.Many2one('overtime.type', domain="[('type', '=', type),('duration_type', '=',  duration_type)]")
    public_holiday = fields.Char(string='Public Holiday', readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance')
    work_schedule = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids')
    global_leaves = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids')

    cash_hrs_amount = fields.Float(string='Overtime Amount', readonly=True)
    cash_day_amount = fields.Float(string='Overtime Amount', readonly=True)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)
    overtime_approver_ids = fields.One2many('setu.overtime.approval.user', 'request_id', string="Approvers")
    current_approver_id = fields.Many2one('res.users')
    user_status = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'),
                                    ('refused', 'Refused')], compute="_compute_user_status")

    @api.onchange('employee_id')
    def _get_defaults(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is to get default data of user
        """

        for sheet in self:
            if sheet.employee_id:
                sheet.update({
                    'department_id': sheet.employee_id.department_id.id,
                    'job_id': sheet.employee_id.job_id.id,
                    'manager_id': sheet.sudo().employee_id.parent_id.user_id.id,
                })

    @api.depends('project_id')
    def _get_project_manager(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to update project manager
        """
        for sheet in self:
            if sheet.project_id:
                sheet.update({
                    'project_manager_id': sheet.project_id.user_id.id,
                })

    @api.depends('overtime_approver_ids.status')
    def _compute_user_status(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to set user status
        """
        for approval in self:
            approval.user_status = approval.overtime_approver_ids.filtered(
                lambda approver: approver.related_approval_id == self.env.user).status

    @api.depends('date_from', 'date_to')
    def _get_days(self):
        """
        Author: jatin.babariya@setconsulting.com
        Date: 27/03/25
        Task: Migration from V16 to V18
        Purpose: This method gives total number of hours or days. Calulation of conversion of time  is done
        """
        _logger.debug("Compute _get_days method start")
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'days_no_tmp': hours + (minutes / 60) if sheet.duration_type == 'hours' else days_no,
                })
        _logger.debug("Compute _get_days method end")

    @api.onchange('overtime_type_id')
    def _get_hour_amount(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to calculate overtime amount dependent on hours/ days
        """
        if self.overtime_type_id.rule_line_ids and self.duration_type == 'hours':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_hour:
                        cash_amount = self.contract_id.over_hour * recd.hrs_amount
                        self.cash_hrs_amount = cash_amount
                    else:
                        raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))
        elif self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_day:
                        cash_amount = self.contract_id.over_day * recd.hrs_amount
                        self.cash_day_amount = cash_amount
                    else:
                        raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))

    def submit_to_f(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is called during submit to finance button, it will send request to the manager as well as
                    status will be changed to waiting.
        """
        approvers = self.mapped('overtime_approver_ids').filtered(lambda approver: approver.status == 'draft')
        approvers.write({'status': 'pending'})
        self.write({'current_approver_id': self.overtime_approver_ids.related_approval_id[0]})
        self.overtime_approver_ids[0]._create_activity()
        return self.sudo().write({
            'state': 'f_approve'
        })

    def _get_user_approval_activities(self, user):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to create activity
        """
        domain = [
            ('res_model', '=', 'hr.overtime'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', self.env.ref('ohrms_overtime.mail_activity_data_overtime_approval').id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    def approve(self):
        """
                Author: jatin.babariya@setconsulting.com
                Date: 27/03/25
                Task: Migration from V16 to V18
                Purpose: This method is called during approve button. It bifuracates the process according to the leave
                        or cash. This method will approve the state by the manager
        """

        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': day_hour,
                    'notes': self.desc,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'validate',
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(holiday_vals)
            self.leave_id = holiday.id

        present_approver_index = \
            [index for index, ap in enumerate(self.overtime_approver_ids.related_approval_id, start=0) if
             ap.id == self.current_approver_id.id][0]
        if len(self.overtime_approver_ids.related_approval_id) - 1 != present_approver_index:
            self.write(
                {'current_approver_id': self.overtime_approver_ids.related_approval_id[present_approver_index + 1]})
            approver = self.mapped('overtime_approver_ids').filtered(
                lambda approver: approver.related_approval_id == self.env.user)
            approver.write({'status': 'approved'})
            next_approver = self.overtime_approver_ids.filtered(lambda x: x.status == 'pending')
            next_approver[0]._create_activity()
            self._get_user_approval_activities(user=self.env.user)
        else:
            self.write({'current_approver_id': False})
            approver = self.mapped('overtime_approver_ids').filtered(
                lambda approver: approver.related_approval_id == self.env.user)
            approver.write({'status': 'approved'})
            self._get_user_approval_activities(user=self.env.user)
        if len(set(self.overtime_approver_ids.mapped('status'))) == 1 and \
                list(set(self.overtime_approver_ids.mapped('status')))[0] == 'approved':
            self.sudo().write({'state': 'approved'})
        else:
            self.sudo().write({'state': 'f_approve'})

    def reject(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to reject an approval and change the state to refused
        """

        self.message_post(body=_(f"Overtime Approval Reject by {self.env.user.name}"))
        self.state = 'refused'
        approver = self.mapped('overtime_approver_ids').filtered(
            lambda approver: approver.related_approval_id == self.env.user)
        approver.write({'status': 'refused'})

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method checks whether date is not overlapped, if date is overlapped it will throw validation
                     error
        """
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))

    @api.model_create_multi
    def create(self, values):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to set overtime_approver_ids
        """
        for vals in values:
            seq = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
            vals['name'] = seq
        res = super(HrOverTime, self.sudo()).create(values)
        # approvers = res.mapped('overtime_approver_ids')
        # approvers.status = 'draft'
        approver_ids = []
        for approver in res.overtime_type_id.related_approval_ids:
            approver_ids.append((0, 0, {'request_id': res.id, 'status': 'draft',
                                        'related_approval_id': approver.related_approval_id.id}))
        res.write({'overtime_approver_ids': approver_ids})
        return res

    def write(self, vals):
        overtime_type_id = vals.get('overtime_type_id', False)
        if overtime_type_id:
            for record in self:
                overtime_type_id = record.env['overtime.type'].browse(overtime_type_id)
                approver_ids = [(2, app.id) for app in record.overtime_approver_ids]
                for approver in overtime_type_id.related_approval_ids:
                    approver_ids.append((0, 0, {'request_id': record.id, 'status': 'draft',
                                                'related_approval_id': approver.related_approval_id.id}))
                vals.update({'overtime_approver_ids': approver_ids})

        return super(HrOverTime, self.sudo()).write(vals)

    def unlink(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to raise validation during deletion of record
        """
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete till request which is not in draft state.'))
        return super(HrOverTime, self).unlink()

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_date(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: In this method, it will check whether the day/ hour you are taking leave falls in any holiday or not.
                     and will also update the attendances.
        """
        holiday = False
        if self.contract_id and self.date_from and self.date_to:
            for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
                leave_dates = pd.date_range(leaves.date_from, leaves.date_to).date
                overtime_dates = pd.date_range(self.date_from, self.date_to).date
                for over_time in overtime_dates:
                    for leave_date in leave_dates:
                        if leave_date == over_time:
                            holiday = True
            if holiday:
                self.write({
                    'public_holiday': 'You have Public Holidays in your Overtime request.'})
            else:
                self.write({'public_holiday': ' '})
            hr_attendance = self.env['hr.attendance'].search(
                [('check_in', '>=', self.date_from),
                 ('check_in', '<=', self.date_to),
                 ('employee_id', '=', self.employee_id.id)])
            self.update({
                'attendance_ids': [(6, 0, hr_attendance.ids)]
            })
