from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class RFMSegmentTeamConf(models.Model):
    _name = 'rfm.segment.team.configuration'
    _description = 'RFM Segment Team Configuration'

    segment_id = fields.Many2one(comodel_name='setu.rfm.segment', required=True, ondelete='cascade')
    from_amount = fields.Float(required=True, group_operator=False,
                               default=lambda self: self.get_max_value('to_amount')[0])
    to_amount = fields.Float(required=True, group_operator=False,
                             default=lambda self: self.get_max_value('to_amount')[1])
    from_frequency = fields.Integer(required=True, group_operator=False,
                                    default=lambda self: self.get_max_value('to_frequency')[0])
    to_frequency = fields.Integer(required=True, group_operator=False,
                                  default=lambda self: self.get_max_value('to_frequency')[1])
    from_days = fields.Integer(required=True, string='Recency From Past X Days', group_operator=False, default=0)
    to_days = fields.Integer(required=True, string='Recency To Past X Days', group_operator=False,
                             default=lambda self: self.get_to_days())
    team_id = fields.Many2one(comodel_name='crm.team', required=True, ondelete='cascade')
    from_atv = fields.Float(required=True, group_operator=False,
                            default=lambda self: self.get_max_value('to_atv')[0])
    to_atv = fields.Float(required=True, group_operator=False,
                          default=lambda self: self.get_max_value('to_atv')[1])

    def get_to_days(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : provide a constant value representing the number of days in a year
        """
        return 365

    def get_max_value(self, field_name):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to find the highest existing value for particular team
        """
        team = self.env.context.get('selected_team', False)
        if team:
            rules = self.search([('team_id', '=', team)])
            vals = rules.mapped(field_name)
            max_val = 0
            if vals:
                max_val = max(vals)
            next_val = max_val + 1
            return next_val, next_val + 1
        return 0, 0

    @api.constrains('segment_id', 'from_amount', 'to_amount', 'from_frequency', 'to_frequency', 'from_days', 'to_days',
                    'from_atv', 'to_atv')
    def validation(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : validate the values of fields to prevent conflicts
        """
        errors = ''
        if self.search([('id', '!=', self.id),
                        ('from_amount', '=', self.from_amount),
                        ('to_amount', '=', self.to_amount),
                        ('from_days', '=', self.from_days),
                        ('to_days', '=', self.to_days),
                        ('from_frequency', '=', self.from_frequency),
                        ('to_frequency', '=', self.to_frequency),
                        ('from_atv', '=', self.from_atv),
                        ('to_atv', '=', self.to_atv),
                        ('team_id', '=', self.team_id.id)
                        ]):
            errors += '• Duplicate rule found for other segment. Please configure rule with different values.\n'

        if self.from_amount > self.to_amount:
            errors += '• From Amount must be less or equal to To Amount.\n'

        if self.to_days <= 0:
            errors += '• To Days must be greater than zero.\n'

        if self.from_frequency > self.to_frequency:
            errors += '• From Frequency must be less or equal to To Frequency.\n'

        if self.from_atv > self.to_atv:
            errors += '• From ATV must be less or equal to To ATV.\n'

        if errors:
            raise ValidationError(_(errors))
