from odoo import api, fields, models


class CustomCateloges(models.Model):
    _name = 'loading.port.cateloges'
    _description = 'LoadingPortCateloges'

    name = fields.Char("Loading Port Name")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
