from odoo import fields, models, api


class SetuAdvanceBudgetForecastedRecreationPeriods(models.Model):
    _name = 'setu.advance.budget.forecasted.recreation.periods'
    _description = 'Recreation Budget Periods'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    forecasted_type = fields.Selection(string='Forecasted Type',
                                       selection=[('planned', 'Planned'), ('actual', 'Actual')], default="planned",
                                       required=True)

    setu_advance_budget_forecasted_recreation_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted.recreation', string='Recreation Budget', required=False)

