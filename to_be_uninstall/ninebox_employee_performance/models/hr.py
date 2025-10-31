# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2017-Present CodersFort. (<https://codersfort.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://codersfort.com/>
#################################################################################

import base64
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource


class EmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    emp_perf_rep_lines = fields.One2many('employee.performance.report','employee_id', string="Employee Performance Report")
    performance_count = fields.Integer(compute='_compute_performance', string='Performance Count', default=0)    
    
    def _compute_performance(self):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: To get number of count of performance record for an employee
        """
        self.ensure_one()
        for record in self:
            performance = self.env['employee.performance'].sudo().search([('employee_id','=',self.id)]).ids
            record.performance_count = len(performance)

class Employee(models.Model):
    _inherit = "hr.employee"

    def action_view_performance(self):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: (1) This method is of smart button (performance) call from employee view
        """
        action = {
            'name': _('Employee Performance(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.performance',
            'target': 'current',
        }
        employee_performance_ids = self.env['employee.performance'].sudo().search([('employee_id','=',self.id)]).ids
        if len(employee_performance_ids) == 1:
            action['res_id'] = employee_performance_ids[0]
            action['view_mode'] = 'form'
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', employee_performance_ids)]
        return action

    def get_domain_for_child_ids(self):
        """
        author : smith ponda
        purpose : this method will return the domain of child ids of current user for employee performance
        :return:
        """
        child_ids = []
        ch_ids = self.child_ids
        while ch_ids:
            child_ids.extend(ch_ids.ids)
            ch_ids = ch_ids.child_ids

        domain = [('employee_id', 'in', child_ids)]
        return domain
