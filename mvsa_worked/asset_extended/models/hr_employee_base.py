from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    asset_ids = fields.One2many('account.asset', 'employee_id', string="Assets")
    setu_authorizer_id = fields.Many2one('hr.employee', string="AUTORIZA")
    setu_issuer_id = fields.Many2one('hr.employee', string="EMISOR")