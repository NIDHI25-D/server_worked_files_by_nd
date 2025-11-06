from odoo import fields, models, api, _


class RFMRuleCopy(models.TransientModel):
    _name = 'copy.rule.conf'
    _description = 'Copy Rule Configuration'

    copy_rules_from = fields.Selection(lambda self: self.get_selection_values(), string='Copy Rules From',
                                       default='Company')
    rule_company_id = fields.Many2one(comodel_name='res.company')
    rule_team_id = fields.Many2one(comodel_name='crm.team')

    copy_rules_to = fields.Selection(lambda self: self.get_selection_values(), string='Copy Rules To',
                                     default='Company')
    to_rule_company_id = fields.Many2one(comodel_name='res.company')
    to_rule_team_id = fields.Many2one(comodel_name='crm.team')

    def get_selection_values(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : determines which options to present in a selection field, allowing for different choices based on user roles
        """
        pass
        if self.env.user.has_group('setu_rfm_analysis.group_sales_team_rfm'):
            return [('Company', 'Company'), ('Sales Team', 'Sales Team')]
        else:
            return [('Company', 'Company')]

    def copy_rules(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : allows users to copy RFM rules from one context (either a company or a sales team) to another
        """
        if self.copy_rules_from == 'Company':
            from_rules = self.env['rfm.segment.configuration'].search([('company_id', '=', self.rule_company_id.id)])
        else:
            from_rules = self.env['rfm.segment.team.configuration'].search([('team_id', '=', self.rule_team_id.id)])

        if self.copy_rules_to == 'Company':
            to_rules = self.env['rfm.segment.configuration'].search([('company_id', '=', self.to_rule_company_id.id)])
        else:
            to_rules = self.env['rfm.segment.team.configuration'].search([('team_id', '=', self.to_rule_team_id.id)])

        for from_rule in from_rules:
            to_rule = to_rules.filtered(lambda r: (r.segment_id.parent_id or r.segment_id) == (
                    from_rule.segment_id.parent_id or from_rule.segment_id))
            to_rule.write({
                'from_days': from_rule.from_days,
                'from_frequency': from_rule.from_frequency,
                'from_amount': from_rule.from_amount,
                'from_atv': from_rule.from_atv,
                'to_days': from_rule.to_days,
                'to_frequency': from_rule.to_frequency,
                'to_amount': from_rule.to_amount,
                'to_atv': from_rule.to_atv
            })

