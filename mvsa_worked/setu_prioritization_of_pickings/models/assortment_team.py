from odoo import fields, models, api,_
from odoo.exceptions import ValidationError

class AssortmentTeam(models.Model):
    _name = 'assortment.team'

    name = fields.Char(string="Name",copy=False)
    warehouse_team_type_id = fields.Many2one('assortment.team.types',string="Warehouse Team type")
    responsible_id = fields.Many2one('hr.employee',string="Responsible",copy=False)
    members_ids = fields.Many2many('res.users', 'res_users_prioritization_of_pickings_rel',string='Members',copy=False)
    suggested_complex_id = fields.Many2one('complexity.levels',string="Suggested Complex",copy=False)
    available = fields.Boolean(string="Available",default=False)
    active= fields.Boolean(string="Active",default=True)
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
    assortment_team_priority = fields.Integer(string="Team sequence",related='suggested_complex_id.complexity_sequence')

    @api.onchange('members_ids')
    def _onchange_members_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/03/25
            Task: Migration to v18 from v16
            Purpose: Fetch all users that have been assigned to other records and exclude the users assigned to other records
        """
        assigned_member_ids = self.search([]).mapped('members_ids.id')
        return {'domain': {'members_ids': [('id', 'not in', assigned_member_ids)]}}

    @api.constrains('members_ids')
    def check_member_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/03/25
            Task: Migration to v18 from v16
            Purpose: It will allow only 2 records for the members
        """
        if len(self.members_ids) > 2:
            raise ValidationError(_("You can't add more than 2 members"))
