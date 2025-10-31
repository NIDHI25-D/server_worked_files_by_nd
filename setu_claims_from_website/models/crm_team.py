from odoo import fields, models, api

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    serviceagent_id = fields.Many2one('res.users', string='Service Agent')