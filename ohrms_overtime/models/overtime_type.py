from dateutil import relativedelta
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class HrOverTimeType(models.Model):
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char('Name')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')])

    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type', domain="[('id', 'in', leave_compute)]")
    leave_compute = fields.Many2many('hr.leave.type', compute="_get_leave_type")
    rule_line_ids = fields.One2many('overtime.type.rule', 'type_line_id')
    overtime_type = fields.Selection([('add', 'Add'), ('sub', 'Subtract')], string="Overtime Type", default="add",
                                     required=True)
    overtime_request_id = fields.Many2one('hr.overtime', string="Request", ondelete='cascade', check_company=True)
    related_approval_ids = fields.One2many('setu.overtime.approval.user', 'overtime_approval_id',
                                           string="Overtime Approves")
    user_id = fields.Many2one('res.users')
    department_id = fields.Many2one('hr.department', string='Department')

    @api.onchange('duration_type')
    def _get_leave_type(self):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used to get overtime type
        """
        _logger.debug("Compute _get_leave_type method start")
        dur = ''
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute = ids
        _logger.debug("Compute _get_leave_type method end")

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """
            Author: jatin.babariya@setconsulting.com
            Date: 27/03/25
            Task: Migration from V16 to V18
            Purpose: This method is used extend domain
        """
        if self._context.get('default_model') == 'hr_overtime':
            employee_obj = self.env['hr.employee'].browse(self._context.get('default_employee_id'))
            if employee_obj:
                id = employee_obj.department_id.id
                domain.extend([('department_id', '=', id)])
        res = super(HrOverTimeType, self)._search(domain, offset, limit, order)
        return res
