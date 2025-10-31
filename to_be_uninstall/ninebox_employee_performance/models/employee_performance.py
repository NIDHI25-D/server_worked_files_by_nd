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


class EmployeePerformance(models.Model):
    _name = "employee.performance"
    _description = "Employee Performance"
    _rec_name = "employee_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.returns('self')
    def _default_employee_get(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def _default_period_id(self):
        return self.env['review.period.timeline'].search([], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee_get)
    period_id = fields.Many2one('review.period.timeline', string="Review Period", default=_default_period_id,
                                required=True)
    review_schedule_id = fields.Many2one(related='period_id.review_schedule_id', string="Review Year", readonly=True)
    emp_asses_ques_rev_ids = fields.One2many('employee.assessment.questions.review', 'performance_id',
                                             'Employee Assessment questions Review')
    mgr_asses_ques_rev_ids = fields.One2many('manager.assessment.questions.review', 'performance_id',
                                             'Manager Assessment questions Review')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submitted', 'Submitted'),
        ('completed', "Completed"),
        ('reset', "Reset"),
    ], default='draft', tracking=True)
    x_rate = fields.Integer(string="X Rating")
    y_rate = fields.Integer(string="Y Rating")

    _sql_constraints = [
        ('employee_period_uniq', 'UNIQUE(employee_id, period_id)', 'The Period must be unique for an Employee')
    ]

    def _valid_field_parameter(self, field, name):
        return name == 'track_visibility' or name == 'tracking' or super()._valid_field_parameter(field, name)

    def get_users_from_group(self, group_id):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: group_id = manager of ninebox performance
                     return user_ids (By whom having group of ninebox performance manager)
        """
        users_ids = []
        sql_query = """select uid from res_groups_users_rel where gid = %s"""
        params = (group_id,)
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchall()
        for users_id in results:
            users_ids.append(users_id[0])
        return users_ids

    def action_submit(self):
        """
            Author: udit@setuconsulting
            Date: 31/01/23
            Task: Agrobolder migration
            Purpose: (1) To chnage the state to submit
                         if performance have self assessment records and sum of rating greater than 0
                     (2) raise user error if self assessment record does have record but not having record of rating
        """
        if self.emp_asses_ques_rev_ids:
            sum_emp_asses_ques_rev_ids = 0
            for rating in self.emp_asses_ques_rev_ids:
                if rating.rating_id:
                    sum_emp_asses_ques_rev_ids += int(rating.rating_id.rate)
                else:
                    raise UserError(_('Assesment Rating Should Not Be Blank.'))
            if sum_emp_asses_ques_rev_ids > 0:
                self.state = 'submitted'
                ninebox_manager_id = self.env['ir.model.data']._xmlid_to_res_id(
                    'ninebox_employee_performance.group_ninebox_performance_manager')
                group_hr_manager_ids = self.get_users_from_group(ninebox_manager_id)
                manager_ids = list(set(group_hr_manager_ids))
                self.message_subscribe(manager_ids)
                body = _(
                    "This Self Assessment has been created from: <a href=# data-oe-model=employee.performance data-oe-id=%d>%s</a> (%s)") % (
                       self.id, self.employee_id.name, self.period_id.assessment_period)
                subject = _("Self Assessment has been created")
                self.message_post(body=body, subject=subject, message_type="notification",
                                  author_id=self.env.user.partner_id.id)

    def action_completed(self):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: To create employee performance report
                     To change the stage to complete
        """
        employee_performance_report_obj = self.env['employee.performance.report']

        if self.emp_asses_ques_rev_ids:
            len_emp_asses_ques_rev_ids = int(len(self.emp_asses_ques_rev_ids))
            sum_emp_asses_ques_rev_ids = 0
            for rating in self.emp_asses_ques_rev_ids:
                if rating.rating_id:
                    sum_emp_asses_ques_rev_ids += int(rating.rating_id.rate)
                else:
                    raise UserError(_('Assesment Rating Should Not Be Blank.'))
            x_rate = round(sum_emp_asses_ques_rev_ids / len_emp_asses_ques_rev_ids)
            self.x_rate = x_rate
        else:
            raise UserError(_('There is not any employee assessment question for the period.'))

        if self.mgr_asses_ques_rev_ids:
            len_mgr_asses_ques_rev_ids = int(len(self.mgr_asses_ques_rev_ids))
            sum_mgr_asses_ques_rev_ids = 0
            for rating in self.mgr_asses_ques_rev_ids:
                if rating.rating_id:
                    sum_mgr_asses_ques_rev_ids += int(rating.rating_id.rate)
                else:
                    raise UserError(_('Assesment Rating Should Not Be Blank.'))
            y_rate = round(sum_mgr_asses_ques_rev_ids / len_mgr_asses_ques_rev_ids)
            self.y_rate = y_rate
        else:
            raise UserError(_('There is not any manager assessment question for the period.'))

        employee_performance_report_obj.sudo().create({
            'employee_id': self.employee_id.id,
            'assessment_period': self.period_id.id,
            'pot_per_rate': str(self.y_rate) + '_' + str(self.x_rate),
        })
        self.state = 'completed'

    def action_reset(self):
        """
            Author: udit@setuconsulting
            Date: 31/01/23
            Task: Agrobolder migration
            Purpose: To reset to draft stage
                     To unlink performance report record
        """
        employee_performance_report_obj = self.env['employee.performance.report'].sudo().search([
            ('employee_id', '=', self.employee_id.id), ('assessment_period', '=', self.period_id.id)
        ])
        if employee_performance_report_obj:
            employee_performance_report_obj.sudo().unlink()
        self.write({
            'state': 'draft',
            'x_rate': False,
            'y_rate': False,
        })

    def unlink(self):
        for record in self:
            employee_performance_report_obj = self.env['employee.performance.report'].sudo().search([
                ('employee_id', '=', record.employee_id.id), ('assessment_period', '=', record.period_id.id)])
            if employee_performance_report_obj:
                employee_performance_report_obj.unlink()
        return super(EmployeePerformance, self).unlink()

    @api.onchange('period_id')
    def onchange_period_id(self):
        if self.emp_asses_ques_rev_ids or self.mgr_asses_ques_rev_ids:
            for record in self.emp_asses_ques_rev_ids:
                self.emp_asses_ques_rev_ids = [(2, record.id)]
            for record in self.mgr_asses_ques_rev_ids:
                self.mgr_asses_ques_rev_ids = [(2, record.id)]

        emp_questions_review = []
        mgr_questions_review = []

        emp_questions_obj = self.env['employee.assessment.questions'].sudo().search(
            [('period_id', '=', self.period_id.id)])
        mgr_questions_obj = self.env['manager.assessment.questions'].sudo().search(
            [('period_id', '=', self.period_id.id)])
        for record in emp_questions_obj:
            review_values = {
                'period_id': self.period_id.id,
                'assessment_question_id': record.id,
            }
            emp_questions_review.append((0, 0, review_values))
        self.emp_asses_ques_rev_ids = emp_questions_review

        for record in mgr_questions_obj:
            review_values = {
                'period_id': self.period_id.id,
                'assessment_question_id': record.id,
            }
            mgr_questions_review.append((0, 0, review_values))
        self.mgr_asses_ques_rev_ids = mgr_questions_review

    @api.onchange('emp_asses_ques_rev_ids')
    def _get_emp_rating_ids(self):
        for record in self.emp_asses_ques_rev_ids:
            rating_ids = record.assessment_question_id.rating_id
            ratings = []
            for rating in rating_ids:
                ratings.append(rating.id)
            record.update({'rating_ids': [(6, 0, ratings)]})

    @api.onchange('mgr_asses_ques_rev_ids')
    def _get_mgr_rating_ids(self):
        for record in self.mgr_asses_ques_rev_ids:
            rating_ids = record.assessment_question_id.rating_id
            ratings = []
            for rating in rating_ids:
                ratings.append(rating.id)
            record.update({'rating_ids': [(6, 0, ratings)]})


class EmployeeAssessmentQuestionsReview(models.Model):
    _name = "employee.assessment.questions.review"
    _description = "Employee Assessment questions Review"
    _rec_name = "assessment_question_id"

    performance_id = fields.Many2one('employee.performance', ondelete='cascade')
    employee_id = fields.Many2one(related='performance_id.employee_id', string='Employee', store=True)
    period_id = fields.Many2one('review.period.timeline', string="Review Period")
    assessment_period = fields.Char(related='period_id.assessment_period', readonly=True, store=True, index='trigram')
    assessment_question_id = fields.Many2one('employee.assessment.questions', string="Assessment Question")
    rating_ids = fields.Many2many('assessment.rating', store=True)
    rating_id = fields.Many2one('assessment.rating', string="Assesment Rating")
    assessment_comment = fields.Text('Comment', index='trigram')


class ManagerAssessmentQuestionsReview(models.Model):
    _name = "manager.assessment.questions.review"
    _description = "Manager Assessment questions Review"
    _rec_name = "assessment_question_id"

    performance_id = fields.Many2one('employee.performance', ondelete='cascade')
    employee_id = fields.Many2one(related='performance_id.employee_id', string='Employee', store=True)
    period_id = fields.Many2one('review.period.timeline', string="Review Period")
    assessment_period = fields.Char(related='period_id.assessment_period', readonly=True, store=True, index='trigram')
    assessment_question_id = fields.Many2one('manager.assessment.questions', string="Assessment Question")
    rating_ids = fields.Many2many('assessment.rating', store=True)
    rating_id = fields.Many2one('assessment.rating', string="Assesment Rating")
    assessment_comment = fields.Text('Comment', index='trigram')
