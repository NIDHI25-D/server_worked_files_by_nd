from odoo import models, fields, api


class ClaimStateHistory(models.Model):
    _name = 'claim.state.history'
    _order = 'id asc'
    _description = "Claim State History"

    stage_id = fields.Many2one('crm.claim.stage', string="Stage")
    claim_id = fields.Many2one('crm.claim', string="Claim")
