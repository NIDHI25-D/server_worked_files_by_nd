from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super(HrEmployee, self).create(vals_list)

    def write(self, vals):
        self.env.registry.clear_cache()
        return super(HrEmployee, self).write(vals)

    def get_stages(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose: This method is used to get departments from the menu.
        """
        if self.env.user.has_group('setu_recruitment_enhancement.supervisior_group_hr_recruitment_applications'):
            return [(1, '=', 1)]
        list_of_stage = []
        employee_id = self.env.user.employee_id
        department_id = employee_id.department_id.id
        stages = self.env['hr.recruitment.stage'].search([])
        if employee_id and department_id:
            stages_with_departments = stages.department_ids
            if stages_with_departments:
                list_of_stage = stages.filtered(lambda x: x.department_ids and department_id in x.department_ids.ids).ids
                domain = [('id', 'in', list_of_stage)]
            else:
                domain = [('id', 'in', stages.ids)]
        else:
            domain = [('id', 'in', [])]

        return domain
