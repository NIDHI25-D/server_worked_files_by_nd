from odoo import api, fields, models, _
from ast import literal_eval
import datetime

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_manager_id = fields.Many2one('hr.employee', string="HR Manger")
    hr_employee_ids = fields.Many2many('hr.employee',string= "Employees")
    cutover_date = fields.Date(string="Cutover Date")

    @api.model
    def get_values(self):
        """
            Author: jatin@setconsulting
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose:  Inherit get values method to get values.
        """
        res = super(ResConfigSettings, self).get_values()
        hr_manager_id = self.env['ir.config_parameter'].sudo().get_param('setu_employee_attendance_report.hr_manager_id', False)
        hr_employee_ids = self.env['ir.config_parameter'].sudo().get_param('setu_employee_attendance_report.hr_employee_ids','[]')
        cutover_date = self.env['ir.config_parameter'].sudo().get_param('setu_employee_attendance_report.cutover_date',False)
        res.update(hr_manager_id=int(hr_manager_id) if hr_manager_id else hr_manager_id,
                   hr_employee_ids=[(6, 0, literal_eval(hr_employee_ids))],
                   cutover_date=cutover_date)
        return res

    @api.model
    def set_values(self):
        """
            Author: jatin@setconsulting
            Date: 02/04/25
            Task: Migration from V16 to V18
            Purpose:  Inherit set values method to set values.
        """
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('setu_employee_attendance_report.hr_manager_id', self.hr_manager_id.id or False)
        self.env['ir.config_parameter'].set_param('setu_employee_attendance_report.hr_employee_ids',
                                                  self.hr_employee_ids.ids or [])
        self.env['ir.config_parameter'].set_param('setu_employee_attendance_report.cutover_date',
                                                  self.cutover_date or False)
        return res
