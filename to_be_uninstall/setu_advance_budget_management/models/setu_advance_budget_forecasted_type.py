from odoo import fields, models, api


class SetuAdvanceBudgetForeCastedType(models.Model):
    _name = 'setu.advance.budget.forecasted.type'
    _description = 'Advance Budget Forecasted Type'

    name = fields.Char(string="Name")
