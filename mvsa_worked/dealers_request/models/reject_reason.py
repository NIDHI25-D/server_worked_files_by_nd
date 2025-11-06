from odoo import fields, models, api


class RejectReason(models.Model):

    _name = "reject.reason"
    _description = 'Reject Reason'
    _rec_name = 'name'

    name = fields.Char(string="Reject Reason")