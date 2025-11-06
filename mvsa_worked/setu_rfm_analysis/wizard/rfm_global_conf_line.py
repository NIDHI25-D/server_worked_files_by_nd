from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class RFMGlobalConfLine(models.TransientModel):
    _name = 'rfm.global.conf.line'
    _description = 'RFM Global Conf. Line'

    global_id = fields.Many2one(comodel_name='rfm.global.conf')
    segment_id = fields.Many2one(comodel_name='setu.rfm.segment')
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
    from_atv = fields.Float(required=True, group_operator=False,
                            default=lambda self: self.get_max_value('to_atv')[0])
    to_atv = fields.Float(required=True, group_operator=False,
                          default=lambda self: self.get_max_value('to_atv')[1])

    def get_max_value(self, field_name):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to calculate maximum value
        """
        rules = self.search([])
        vals = rules.mapped(field_name)
        max_val = 0
        if vals:
            max_val = max(vals)
        next_val = max_val + 1
        return next_val, next_val + 1

    def get_to_days(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : provide a constant value representing the number of days in a year
        """
        return 365

    @api.constrains('segment_id', 'from_amount', 'to_amount', 'from_frequency', 'to_frequency', 'from_days', 'to_days',
                    'from_atv', 'to_atv')
    def validation(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to ensure that no conflicting or incorrect data is saved
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
                        ('global_id', '=', self.global_id.id)
                        ]):
            self.search([('global_id', '=', self.global_id.id)])
            errors += '• Duplicate rule found for other segment. Please configure rule with different values.\n'

        if self.from_amount > self.to_amount:
            errors += '• From Amount must be less or equal to To Amount.\n'

        if self.to_days <= 0:
            errors += '• To Days must be greater than zero.\n'

        if self.from_frequency > self.to_frequency:
            errors += '• From Frequency must be less or equal to To Frequency.\n'

        if self.from_atv > self.to_atv:
            errors += '• From ATV must be less or equal to To ATV.\n'

        if self.from_days > self.to_days:
            errors += '• Recency From Past X Days must be less or equal to Recency To Past X Days.\n'

        if errors:
            raise ValidationError(_(errors))
