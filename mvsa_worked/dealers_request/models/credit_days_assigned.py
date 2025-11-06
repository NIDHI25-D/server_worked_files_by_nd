from odoo import fields, models, api


class CreditDaysAssigned(models.Model):

    _name = "credit.days.assigned"
    _description = 'Credit Days Assigned'
    _rec_name = 'name'

    name = fields.Char(string="Name")