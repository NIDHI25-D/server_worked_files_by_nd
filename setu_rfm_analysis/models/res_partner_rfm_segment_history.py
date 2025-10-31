from odoo import fields, models, api, _


class ResPartnerRFMSegmentHistory(models.Model):
    _name = 'res.partner.rfm.segment.history'
    _description = """
    Customer RFM segment history table will automatically add records in the table when the customer RFM score will be 
    changed to another one and if the segment value has been changed
    """
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer")
    history_date = fields.Date(string="History Date")
    old_rfm_segment_id = fields.Many2one(comodel_name="setu.rfm.segment", string="Old RFM Segment",
                                         help="Customer's Old RFM segment")
    new_rfm_segment_id = fields.Many2one(comodel_name="setu.rfm.segment", string="New RFM Segment",
                                         help="Customer's New RFM segment")
    old_rfm_score_id = fields.Many2one(comodel_name="setu.rfm.score", string="Old RFM Score",
                                       help="Customer's Old RFM score")
    new_rfm_score_id = fields.Many2one(comodel_name="setu.rfm.score", string="New RFM Score",
                                       help="Customer's New RFM score")
    old_segment_rank = fields.Integer(string="Old Segment Rank")
    new_segment_rank = fields.Integer(string="New Segment Rank")
    engagement_direction = fields.Integer(string="Engagement Direction (Up / Down / Consistent)", help="""
        It shows the customer's engagement activities with the business, whether it's increased, decreased or consistent
    """)