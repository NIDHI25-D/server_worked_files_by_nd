from odoo import api, fields, models, _

class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    department_ids = fields.Many2many('hr.department', 'stage_department_tab_rel', 'stage_id', 'department_id',
                                      string='Departments')

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super(HrRecruitmentStage, self).create(vals_list)

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/01/25
            Task: Migration from V16 to V18
            Purpose: if adding the department into department_ids, then it does not have to contain
                any applications if it has then it will give earning.
        """
        self.env.registry.clear_cache()
        not_selected_department = []
        for record in self:
            hr_applicant_ids = self.env['hr.applicant'].search([('stage_id', '=', record._origin.id)])
            department_ids = hr_applicant_ids.mapped('department_id')
            for department_id in department_ids:
                if department_id.id not in (
                        vals.get('department_ids')[0] if vals.get(
                            'department_ids') else record._origin.department_ids.ids):
                    not_selected_department.append(department_id.name)
            if not_selected_department:
                raise Warning(
                    _(f"Please select these departments {not_selected_department}.Beacuse some of the applications of these departments are in {record.name} "))
        return super(HrRecruitmentStage, self).write(vals)
