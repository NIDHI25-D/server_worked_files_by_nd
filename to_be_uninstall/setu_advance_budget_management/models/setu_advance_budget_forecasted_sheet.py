from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class SetuAdvanceBudgetForeCastedSheet(models.Model):
    _name = 'setu.advance.budget.forecasted.sheet'
    _description = 'Advance Budget Forecasted Sheet'
    _rec_name = 'setu_advance_budget_forecasted_id'

    planned_amount = fields.Float(string='Planned Amount', compute='_get_total_sheet_line_planned_amount')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    setu_advance_budget_forecasted_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted', string='Budget Forecast', required=False)

    setu_advance_budget_forecasted_sheet_line_ids = fields.One2many(comodel_name='setu.advance.budget.forecasted.sheet.line',   inverse_name='setu_advance_budget_forecasted_sheet_id',string='Budget Forecasted Sheet Line',  required=False)

    @api.depends('setu_advance_budget_forecasted_sheet_line_ids')
    def _get_total_sheet_line_planned_amount(self):
        _logger.debug("Compute _get_total_sheet_line_planned_amount method start")
        for forecasted_sheet_id in self:
            forecasted_sheet_id.planned_amount = sum(forecasted_sheet_line_id.planned_amount for forecasted_sheet_line_id in forecasted_sheet_id.setu_advance_budget_forecasted_sheet_line_ids)
        _logger.debug("Compute _get_total_sheet_line_planned_amount method end")
