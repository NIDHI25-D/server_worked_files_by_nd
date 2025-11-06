from odoo import fields, models


class PartnerSegments(models.Model):
    _name = 'partner.segments'
    _description = 'Partner Segments'

    company_id = fields.Many2one(comodel_name='res.company')
    partner_id = fields.Many2one(comodel_name='res.partner')
    segment_id = fields.Many2one(comodel_name='setu.rfm.segment')
    team_id = fields.Many2one(comodel_name='crm.team')
    score_id = fields.Many2one(comodel_name='setu.rfm.score')
