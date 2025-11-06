from odoo import api, fields, models, _

class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super(HrDepartment, self).create(vals_list)

    def write(self, vals):
        self.env.registry.clear_cache()
        return super(HrDepartment, self).write(vals)
