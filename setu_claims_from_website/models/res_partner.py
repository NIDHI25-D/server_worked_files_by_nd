from odoo import fields, models, api, _

class res_partner(models.Model):
    _inherit = 'res.partner'

    claim_count = fields.Integer(string='# Claims', compute='_compute_claim_count')

    def _compute_claim_count(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: This method will count the claims as per the partner located in the partner->smart button
        """
        for partner in self:
            partner.claim_count = self.env['crm.claim'].search_count(
                [('partner_id', '=', partner.id)])