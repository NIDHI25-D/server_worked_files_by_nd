from odoo import api, fields, models


class CustomAgency(models.Model):
    _name = 'custom.agency'
    _description = 'CustomAgency'

    name = fields.Char("Agency Name")
    customs = fields.Many2one('custom.cateloges', string="Customs")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
