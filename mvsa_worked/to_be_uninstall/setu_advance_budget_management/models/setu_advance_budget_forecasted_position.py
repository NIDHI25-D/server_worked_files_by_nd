from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class SetuAdvanceBudgetForecastedPosition(models.Model):
    _name = 'setu.advance.budget.forecasted.position'
    _description = 'Advance Budget Forecasted Position'
    _rec_name = "start_date"

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    planned_amount = fields.Float(string='Amount')
    amount_in_journal_items = fields.Float(string="Amount in Journal Items")
    difference_with_planned_amount_journal = fields.Float(string="Difference Abs.",
                                                          compute='_compute_amount_diff_percentage')
    difference_with_planned_amount_journal_percentage = fields.Float(string="Difference %",
                                                                     compute='_compute_amount_diff_percentage')

    forecasted_type = fields.Selection(string='Forecasted Type',
                                       selection=[('planned', 'Planned'), ('actual', 'Actual')], default="planned")

    setu_advance_budget_forecasted_sheet_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted.sheet',
                                                              string='Forecast Sheet', required=False)
    setu_advance_budget_forecasted_sheet_line_id = fields.Many2one(
        comodel_name='setu.advance.budget.forecasted.sheet.line', string=' Budget Forecasted Sheet Line',
        required=False)
    setu_advance_budget_forecasted_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted',
                                                        string='Forecast', required=False, related="setu_advance_budget_forecasted_sheet_id.setu_advance_budget_forecasted_id")

    setu_advance_budget_forecasted_budget_state = fields.Selection(related='setu_advance_budget_forecasted_id.state',
                                                                   string='Budget State', store=True, readonly=True)

    account_id = fields.Many2one(comodel_name='account.account',
                                 related="setu_advance_budget_forecasted_sheet_line_id.account_id", string='Account',
                                 required=False, store=True)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',
                                          related="setu_advance_budget_forecasted_sheet_line_id.analytic_account_id",
                                          string='Analytic Account', required=False, store=True)

    def _compute_amount_diff_percentage(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: calculate difference amount and difference percentage
        """
        _logger.debug("Compute _compute_amount_diff_percentage method start")
        for record_id in self:
            if record_id.planned_amount > 0:
                difference_amount = record_id.amount_in_journal_items - record_id.planned_amount
                record_id.difference_with_planned_amount_journal = difference_amount
                record_id.difference_with_planned_amount_journal_percentage = abs((difference_amount / record_id.planned_amount)) * 100
            else:
                record_id.difference_with_planned_amount_journal = 0.0
                record_id.difference_with_planned_amount_journal_percentage = 0.0
        _logger.debug("Compute _compute_amount_diff_percentage method end")
