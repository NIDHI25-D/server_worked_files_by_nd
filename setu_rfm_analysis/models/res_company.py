from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.company'

    take_sales_from_x_days = fields.Integer(string='Sales Of Last X Days', default=365, required=1,
                                            help="For calculation of RFM segment, days inserted here "
                                                 "will be used to fetch past sales data.")
    segment_history_days = fields.Integer(string='Keep Segment History of last X Days', default=365, required=1,
                                          help="RFM Segment History will be kept for days inserted here.")
    segment_configuration_ids = fields.One2many(comodel_name='rfm.segment.configuration', inverse_name='company_id')

    @api.constrains('segment_history_days', 'take_sales_from_x_days')
    def days_constrain(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use :  this method is to validate that the value entered in the take_sales_from_x_days field does not exceed a
        certain threshold (99999 days in this case). This helps to maintain reasonable data input and prevents
        unrealistic values from being saved
        """
        if self.take_sales_from_x_days > 99999:
            raise UserError('Please enter valid number of days in Sales Of Last X Days field.')

    def open_rfm_segment_rules(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use - to facilitate the opening of an RFM segment configuration window, tailored to the current company's context
        """
        action = self.env.ref('setu_rfm_analysis.rfm_score_configuration_act_window').sudo().read()[0]
        action.update({
            'domain': [('company_id', '=', self.id)],
            'display_name': self.name
        })
        return action

