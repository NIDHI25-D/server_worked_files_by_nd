from odoo import fields, models, api, _


class SetuRFMScore(models.Model):
    _name = 'setu.rfm.score'
    _description = "RFM score helps to define RFM segment criteria."

    name = fields.Char(string="RFM Score")
    rfm_segment_id = fields.Many2one(comodel_name="setu.rfm.segment", string="RFM Segment",
                                     help="""Connect RFM score with RFM segment""")
    recency = fields.Selection(selection=[('1', '1'),
                                          ('2', '2'),
                                          ('3', '3'),
                                          ('4', '4')], string="Recency", help=""""
        Recency, Rank your customers according to the number of days since customer's last purchase """)
    frequency = fields.Selection(selection=[('1', '1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4')], string="Frequency", help=""""
            Frequency, Rank your customers according to the number of times customer place an order (ordering frequency) """)
    monetization = fields.Selection(selection=[('1', '1'),
                                               ('2', '2'),
                                               ('3', '3'),
                                               ('4', '4')], string="Monetization", help=""""
            Monetization, Rank your customers according to Customer's total orders value """)

    description = fields.Text(string="Description", help="Customer activity")
    partner_ids = fields.One2many(comodel_name="res.partner", inverse_name="rfm_score_id", string="Customers")
    total_customers = fields.Integer(string="Total Customers", compute='_compute_customers')

    @api.depends('partner_ids')
    def _compute_customers(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to find the total of customers
        """
        for score in self:
            score.total_customers = len(score.partner_ids)

    @api.onchange('recency', 'frequency', 'monetization')
    def onchange_rfm_score(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to calculate score
        """
        recency = self.recency or ''
        frequency = self.frequency or ''
        monetization = self.monetization or ''
        score = recency + frequency + monetization
        self.name = score
