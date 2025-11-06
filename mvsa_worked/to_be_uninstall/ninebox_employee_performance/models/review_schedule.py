# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2017-Present CodersFort. (<https://codersfort.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://codersfort.com/>
#################################################################################

import datetime
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReviewSchedule(models.Model):
    _name = "review.schedule"
    _description = "Review Schedule"
    _order = 'year desc'
    _rec_name = "year"

    @api.model
    def _year_get(self):
        return [(str(num), str(num)) for num in range(1900, (datetime.now().year) + 2)]

    year = fields.Selection(_year_get, string='Year', copy=False)
    period_frequency = fields.Selection([
        ('every_1_months', 'Every 1 Months'),
        ('every_3_months', 'Every 3 Months'),
        ('every_6_months', 'Every 6 Months'),
        ('every_12_months', 'Every 12 Months'), ],
        string='Review Period Frequency', required=True, default='every_3_months', copy=False)
    review_period_timelines = fields.One2many('review.period.timeline', 'review_schedule_id', 'Review Period Timeline',
                                              copy=False)

    def unlink(self):
        """
            Author: udit@setuconsulting
            Date: 26/01/23
            Task: Agrobolder migration
            Purpose: To raise user error to stop to delete record if review schedule record is assigned for any employee
        """
        for record in self:
            employee_performance_obj = self.env['employee.performance'].sudo().search([
                ('review_schedule_id', '=', record.id)])
            if employee_performance_obj:
                raise UserError(_('Review Schedule is already assigned for the Employees.'))
        return super(ReviewSchedule, self).unlink()

    def create_assessment_period(self):

        """
            Author: udit@setuconsulting
            Date: 26/01/23
            Task: Agrobolder migration
            Purpose: create period timeline record on the basis of period frequency
        """
        period_frequency = []
        every_1_months = [str(self.year) + '-JAN-01', str(self.year) + '-FEB-01', str(self.year) + '-MAR-01',
                          str(self.year) + '-APR-01', str(self.year) + '-MAY-01', str(self.year) + '-JUN-01',
                          str(self.year) + '-JUL-01', str(self.year) + '-AUG-01', str(self.year) + '-SEP-01',
                          str(self.year) + '-OCT-01', str(self.year) + '-NOV-01', str(self.year) + '-DEC-01']
        every_3_months = [str(self.year) + '-JAN-01', str(self.year) + '-APR-01', str(self.year) + '-AUG-01',
                          str(self.year) + '-DEC-01']
        every_6_months = [str(self.year) + '-JAN-01', str(self.year) + '-JUN-01']
        every_12_months = [str(self.year) + '-DEC-01']

        for record in self.review_period_timelines:
            self.review_period_timelines = [(2, record.id)]

        if self.year and self.period_frequency:
            if self.period_frequency == 'every_1_months':
                for period in every_1_months:
                    timelines_values = {
                        'review_schedule_id': self.id,
                        'assessment_period': period,
                    }
                    period_frequency.append((0, 0, timelines_values))

            if self.period_frequency == 'every_3_months':
                for period in every_3_months:
                    timelines_values = {
                        'review_schedule_id': self.id,
                        'assessment_period': period,
                    }
                    period_frequency.append((0, 0, timelines_values))

            if self.period_frequency == 'every_6_months':
                for period in every_6_months:
                    timelines_values = {
                        'review_schedule_id': self.id,
                        'assessment_period': period,
                    }
                    period_frequency.append((0, 0, timelines_values))

            if self.period_frequency == 'every_12_months':
                for period in every_12_months:
                    timelines_values = {
                        'review_schedule_id': self.id,
                        'assessment_period': period,
                    }
                    period_frequency.append((0, 0, timelines_values))

            self.sudo().write({
                'review_period_timelines': period_frequency,
            })

    _sql_constraints = [
        ('year_uniq', 'unique (year)', """Year should be unique !"""),
    ]


class ReviewPeriodTimeline(models.Model):
    _name = "review.period.timeline"
    _description = "Review Period Timeline"
    _rec_name = "assessment_period"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    review_schedule_id = fields.Many2one('review.schedule', ondelete="cascade")
    assessment_period = fields.Char('Assessment Period', index='trigram')
    emp_assessment_qtn_ids = fields.One2many('employee.assessment.questions', 'period_id',
                                             'Employee Assessment Questions')
    mgr_assessment_qtn_ids = fields.One2many('manager.assessment.questions', 'period_id',
                                             'Manager Assessment Questions')
    mail_notification = fields.Boolean(string='Mail Notification', default=False)
    state = fields.Selection([
        ('not_send', 'Not Send'),
        ('send', 'Send'),
    ], default='not_send')

    _sql_constraints = [
        ('period_uniq', 'unique (assessment_period)', """Period should be unique !"""),
    ]

    def unlink(self):
        """
            Author: udit@setuconsulting
            Date: 26/01/23
            Task: Agrobolder migration
            Purpose: To raise user error to stop to delete record if review schedule record is assigned for any employee
        """
        for record in self:
            employee_performance_obj = self.env['employee.performance'].sudo().search([
                ('review_schedule_id', '=', record.review_schedule_id.id)])
            if employee_performance_obj:
                raise UserError(_('Review Schedule is already assigned for some of the Employees.'))
        return super().unlink()

    def create_employees_performance(self):
        """
            Author: udit@setuconsulting
            Date: 26/01/23
            Task: Agrobolder migration
            Purpose: To create employee performance record
        """
        hr_employee_obj = self.env['hr.employee'].sudo().search([])
        emp_assessment_qtn_ids = self.emp_assessment_qtn_ids
        mgr_assessment_qtn_ids = self.mgr_assessment_qtn_ids

        if not emp_assessment_qtn_ids:
            raise UserError(
                _('Employee Assessment Questions is not available for this period, Please create some Questions.'))

        if not mgr_assessment_qtn_ids:
            raise UserError(
                _('Manager Assessment Questions is not available for this period, Please create some Questions.'))

        for employee in hr_employee_obj:

            if employee and self.id:
                emp_questions_review_ids = []
                mgr_questions_review_ids = []

                for record in emp_assessment_qtn_ids:
                    review_values = {
                        'period_id': self.id,
                        'assessment_question_id': record.id,
                        'rating_ids': [(6, 0, [x.id for x in record.rating_id])]
                    }
                    emp_questions_review_ids.append((0, 0, review_values))

                for record in mgr_assessment_qtn_ids:
                    review_values = {
                        'period_id': self.id,
                        'assessment_question_id': record.id,
                        'rating_ids': [(6, 0, [x.id for x in record.rating_id])]
                    }
                    mgr_questions_review_ids.append((0, 0, review_values))

                performance_id = self.env['employee.performance'].create({
                    'employee_id': employee.id,
                    'period_id': self.id,
                    'emp_asses_ques_rev_ids': emp_questions_review_ids,
                    'mgr_asses_ques_rev_ids': mgr_questions_review_ids,
                })

                if self.mail_notification and performance_id and employee.user_id.partner_id.id:
                    body = _(
                        "Employee Performance Record has been created: <a href=# data-oe-model=employee.performance data-oe-id=%d>%s</a>") % (
                               performance_id.id, employee.name)
                    mail = self.env['mail.mail'].create({
                        'body_html': body,
                        'is_notification': True,
                        'state': 'outgoing',
                        'recipient_ids': [(4, employee.user_id.partner_id.id)]
                    })
        self.state = 'send'

    def reset(self):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: To change the stage to 'not_send'
        """
        for record in self:
            employee_performance_obj = self.env['employee.performance'].sudo().search(
                [('review_schedule_id', '=', record.review_schedule_id.id)])
            if employee_performance_obj:
                raise UserError(_('Review Schedule is already assigned for the Employees.'))
            else:
                record.state = 'not_send'


class EmployeeAssessmentQuestions(models.Model):
    _name = "employee.assessment.questions"
    _description = "Employee Assessment Questions"
    _rec_name = "assessment_question"

    active = fields.Boolean(default=True)
    period_id = fields.Many2one('review.period.timeline', string="Period")
    assessment_question = fields.Text('Assessment Question', required=True, index='trigram')
    rating_id = fields.Many2many('assessment.rating', 'emp_assessment_rating', 'qtn_id', 'rating_id',
                                 string="Assesment Rating")


class ManagerAssessmentQuestions(models.Model):
    _name = "manager.assessment.questions"
    _description = "Manager Assessment Questions"
    _rec_name = "assessment_question"

    active = fields.Boolean(default=True)
    period_id = fields.Many2one('review.period.timeline', string="Period")
    assessment_question = fields.Text('Assessment Question', required=True, index='trigram')
    rating_id = fields.Many2many('assessment.rating', 'mgr_assessment_rating', 'qtn_id', 'rating_id',
                                 string="Assesment Rating")


class AssessmentRating(models.Model):
    _name = "assessment.rating"
    _description = "Assessment Rating"
    _rec_name = "name"

    name = fields.Char(string="Rating Name", required=True, index='trigram')
    rate = fields.Integer(string="Rating", required=True)
    color = fields.Integer('Color Index', default=0, help="0-10")

    _sql_constraints = [
        ('name_rate_uniq', 'unique (name,rate)', """Name and Rate should be unique!!"""),
    ]
