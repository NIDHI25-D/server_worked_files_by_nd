from odoo import fields, models, api


class CreditDaysRequest(models.Model):

    _name = "credit.days.requested"
    _description = 'Credit Days Request'
    _rec_name = 'name'

    name = fields.Char(string="Days")