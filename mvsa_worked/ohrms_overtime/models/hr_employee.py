from odoo import api, fields, models

class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee.base'

    is_overtime_approve_director = fields.Boolean("Overtime Approver Director", default=False)

