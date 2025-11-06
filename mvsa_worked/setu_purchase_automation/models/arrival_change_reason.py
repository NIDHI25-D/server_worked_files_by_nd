from odoo import models, fields, api, _


class ArrivalChangeReason(models.Model):
    _name = 'arrival.change.reason'
    _description = 'Arrival Change Reason'
    _rec_name = 'name'

    name = fields.Char(string="Arrival Late")
