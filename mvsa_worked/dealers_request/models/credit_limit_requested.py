from odoo import fields, models, api


class CreditLimitRequested(models.Model):

    _name = "credit.limit.requested"
    _description = 'Credit Limit Requested'
    _rec_name = 'name'

    name = fields.Integer(string="Name")

    def name_get(self):
        res = []
        for record in self:
            name = f'{record.name:,}'
            res.append((record.id, name))
        return res