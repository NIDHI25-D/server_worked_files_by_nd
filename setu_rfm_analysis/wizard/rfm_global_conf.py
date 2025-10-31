from odoo import fields, models, api, _


class RFMGlobalConf(models.TransientModel):
    _name = 'rfm.global.conf'
    _description = 'RFM Global Conf.'

    global_for_company = fields.Boolean(default=True)
    global_for_sales_team = fields.Boolean(default=True)
    global_rule_lines = fields.One2many(comodel_name='rfm.global.conf.line', inverse_name='global_id')

    @api.model
    def create(self, vals):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to link newly created global configuration records with existing RFM segment templates
        """
        res = super(RFMGlobalConf, self).create(vals)
        segment_templates = self.env['setu.rfm.segment'].sudo().search([('is_template', '=', True)])
        for segment in segment_templates:
            self.env['rfm.global.conf.line'].create({
                'global_id': res.id,
                'segment_id': segment.id
            })
        return res

    def create_open_global_conf_wizard(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : creates a new global configuration record then opens a specific wizard
        """
        self.env['rfm.global.conf.line'].sudo().search([]).unlink()
        res = self.create({})
        action = self.env['ir.actions.act_window']._for_xml_id('setu_rfm_analysis.global_segment_rules_act_window')
        action['res_id'] = res.id
        return action

    def make_global_rule(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it applies global RFM rules to individual companies and sales teams
        """
        if self.global_for_company:
            companies = self.env['res.company'].sudo().search([])
            for c in companies:
                c_rules = self.env['rfm.segment.configuration'].search([('company_id', '=', c.id)])
                for from_rule in self.global_rule_lines:
                    to_rule = c_rules.filtered(lambda r: r.segment_id == from_rule.segment_id)
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
        if self.global_for_sales_team:
            teams = self.env['crm.team'].sudo().search([])
            for t in teams:
                t_rules = self.env['rfm.segment.team.configuration'].search([('team_id', '=', t.id)])
                for from_rule in self.global_rule_lines:
                    to_rule = t_rules.filtered(lambda r: r.segment_id.parent_id == from_rule.segment_id)
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