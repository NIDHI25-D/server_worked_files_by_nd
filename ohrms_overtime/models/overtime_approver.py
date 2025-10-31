from odoo import fields, models, api


class SetuApprovalsUser(models.Model):
    _name = "setu.overtime.approval.user"
    _description = "Setu Overtime Approval User"

    overtime_approval_id = fields.Many2one('overtime.type')
    related_approval_id = fields.Many2one('res.users')
    sequence = fields.Integer()
    request_id = fields.Many2one('hr.overtime')
    status = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending'), ('approved', 'Approved'), ('refused', 'Refused')],
        string="State", default="draft")

    def _create_activity(self):
        if self:
            self = self[0]
            self.request_id.activity_schedule('ohrms_overtime.mail_activity_data_overtime_approval',
                                              user_id=self.related_approval_id.id)

    def approve(self):
        self.request_id.approve(self)

    def refuse(self):
        self.request_id.refuse(self)
