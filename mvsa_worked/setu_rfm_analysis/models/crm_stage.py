from odoo import fields, models, api


class CRMStage(models.Model):
    _inherit = "crm.stage"
    _description = "Customer Segment Is Won"

    is_won = fields.Boolean(string='Is Won')
