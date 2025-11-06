from odoo import fields, models, api, _
from datetime import date


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rfm_segment_id = fields.Many2one(comodel_name="setu.rfm.segment", string="RFM Segment", company_dependent=True,
                                     help="""Connect RFM score with RFM segment""")
    rfm_score_id = fields.Many2one(comodel_name="setu.rfm.score", string="RFM Score", company_dependent=True,
                                   help="RFM score")

    partner_segment_history_ids = fields.One2many(comodel_name="res.partner.rfm.segment.history",
                                                  inverse_name="partner_id",
                                                  string="Customer Segment History")
    rfm_team_segment_ids = fields.One2many(comodel_name='partner.segments', inverse_name='partner_id')
    is_dynamic_rule_enable = fields.Boolean(string='Is Dynamic Rule Enable?', compute='check_is_dynamic_rule_enable')

    def check_is_dynamic_rule_enable(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to check dynamic rule is enable or not
        """
        if self.env.user.has_group('setu_rfm_analysis.group_dynamic_rules'):
            self.is_dynamic_rule_enable = True
        else:
            self.is_dynamic_rule_enable = False

    def create_rfm_segment_history(self, vals):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to create segment history
        """
        rfm_segment_id = self.env['setu.rfm.segment'].search([('id', '=', vals.get('rfm_segment_id', False))])
        new_rank = rfm_segment_id and rfm_segment_id.segment_rank or -1
        old_rank = self.rfm_segment_id.segment_rank
        direction = 0

        if old_rank > new_rank:
            direction = -1
        elif old_rank < new_rank:
            direction = 1
        history_vals = {
            'partner_id': self.id,
            'history_date': date.now(),
            'old_rfm_segment_id': self.rfm_segment_id.id,
            'new_rfm_segment_id': rfm_segment_id or rfm_segment_id.id or False,
            'old_rfm_score_id': self.rfm_score_id.id,
            'new_rfm_score_id': vals.get('rfm_score_id', False),
            'old_segment_rank': old_rank,
            'new_segment_rank': rfm_segment_id and rfm_segment_id.segment_rank or -1,
            'engagement_direction': direction,
        }
        self.env['res.partner.rfm.segment.history'].create(history_vals)

    def open_partner_rfm_segment_history(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to get the segment history of partner
        """
        action = self.env.ref('setu_rfm_analysis.rfm_partner_history_company_wise_act_window').sudo().read()[0]
        action.update({'domain': [('partner_id', '=', self.id)]})
        return action


