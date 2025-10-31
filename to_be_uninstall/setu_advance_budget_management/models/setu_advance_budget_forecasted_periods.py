from odoo import fields, models, api


class SetuAdvanceBudgetForecastedPeriods(models.Model):
    _name = "setu.advance.budget.forecasted.periods"
    _description = 'Advance Budget Forecasted Periods'
    _rec_name = "start_date"

    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End Date',required=True)

    forecasted_type = fields.Selection(string='Forecasted Type', selection=[('planned', 'Planned'),  ('actual', 'Actual')],default="planned",required=True)

    setu_advance_budget_forecasted_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted',string='Budget Forecast',ondelete="cascade",required=False)




