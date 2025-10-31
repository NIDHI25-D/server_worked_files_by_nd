# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2017-Present CodersFort. (<https://codersfort.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://codersfort.com/>
#################################################################################

import datetime
from datetime import datetime, timedelta
from odoo import api, fields, models, _


class EmployeePerformanceReport(models.Model):
    _name = "employee.performance.report"
    _description = "Employee Performance Report"

    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
    employee_name = fields.Char(related="employee_id.name", readonly=False)
    assessment_period = fields.Many2one('review.period.timeline', string="Assessment Period")
    pot_per_rate = fields.Selection([('0_0', '0x0'),
                                     ('1_1', '1x1'), ('1_2', '1x2'), ('1_3', '1x3'),
                                     ('2_1', '2x1'), ('2_2', '2x2'), ('2_3', '2x3'),
                                     ('3_1', '3x1'), ('3_2', '3x2'), ('3_3', '3x3'), ],
                                    string='Peformance Rating', required=True, default='0_0')
    manager_name = fields.Char(string="Manager Name", compute='_compute_manager_name', readonly=False, store=True)
    job_position = fields.Char(string="Job Position", compute='_compute_job_position', readonly=False, store=True)

    @api.depends('assessment_period')
    def _compute_manager_name(self):
        self.ensure_one()
        if self.employee_id:
            self.manager_name = self.employee_id.parent_id.name

    @api.depends('assessment_period')
    def _compute_job_position(self):
        self.ensure_one()
        if self.employee_id:
            self.job_position = self.employee_id.job_id.name

    # @api.multi
    def write(self, values):
        assessment_period = values.get('assessment_period', False)
        record_set = assessment_period and self.env["review.period.timeline"].search(
            [('id', '=', assessment_period)]) or False
        for record in self:
            final_body_string = ""
            if 'assessment_period' in values or 'pot_per_rate' in values or 'manager_name' in values or 'job_position' in values:
                if values.get('assessment_period', False) and record_set:
                    body_string = f"<strong>Assessment Period: <strong/>{record.assessment_period.display_name} --> {record_set.display_name}<br />"
                    final_body_string += body_string
                if values.get('pot_per_rate', False):
                    value_in_list = record.get_selection_field_value('pot_per_rate')
                    pot_per_rate = [rec[1] for rec in value_in_list if rec[0] == record.pot_per_rate]
                    pot_per_rate = pot_per_rate and pot_per_rate[0] or record.pot_per_rate

                    new_pot_per_rate = [rec[1] for rec in value_in_list if rec[0] == values.get('pot_per_rate')]
                    new_pot_per_rate = new_pot_per_rate and new_pot_per_rate[0] or values.get('pot_per_rate')
                    body_string = f"<strong>Performance Rating: <strong/> {pot_per_rate} --> {new_pot_per_rate}<br />"
                    final_body_string += body_string
                if values.get('manager_name', False):
                    body_string = f"<strong>Manager Name: <strong/> {record.manager_name} --> {values.get('manager_name')}<br />"
                    final_body_string += body_string
                if values.get('job_position', False):
                    body_string = f"<strong>Job Position: <strong/> {record.job_position} --> {values.get('job_position')}<br />"
                    final_body_string += body_string
            employee = record.employee_id
            if employee and final_body_string:
                employee.message_post(body=final_body_string, subject='Set Log')
        return super(EmployeePerformanceReport, self).write(values)

    def get_selection_field_value(self, field):
        return self.fields_get().get(field, {}).get('selection', [])
