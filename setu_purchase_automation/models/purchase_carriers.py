from odoo import api, fields, models


class CustomCateloges(models.Model):
    _name = 'purchase.carriers'
    _description = 'purchaseCarriers'

    name = fields.Char("Carrier Name")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
