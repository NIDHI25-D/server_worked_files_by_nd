from odoo import api, fields, models


class CustomCateloges(models.Model):
    _name = 'custom.cateloges'
    _description = 'CustomCateloges'

    name = fields.Char("Custom Name")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
