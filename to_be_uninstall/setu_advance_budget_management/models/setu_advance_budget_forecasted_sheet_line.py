from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class SetuAdvanceBudgetForeCastedSheetLine(models.Model):
    _name = 'setu.advance.budget.forecasted.sheet.line'
    _description = 'Advance Budget Forecasted Sheet Line'
    _rec_name = 'setu_advance_budget_forecasted_sheet_id'

    @api.model
    def default_get(self, fields):
        res = super(SetuAdvanceBudgetForeCastedSheetLine, self).default_get(fields)
        setu_advance_budget_forecasted_obj = self.env['setu.advance.budget.forecasted']

        setu_advance_budget_forecasted_position_obj = self.env['setu.advance.budget.forecasted.position']
        ctx = dict(self.env.context)

        if ctx.get('default_setu_advance_budget_forecasted_id'):
            setu_advance_budget_forecasted_id = setu_advance_budget_forecasted_obj.browse(
                ctx.get('default_setu_advance_budget_forecasted_id'))
            if setu_advance_budget_forecasted_id:
                forecasted_position_lst = []
                for setu_advance_budget_forecasted_periods_id in setu_advance_budget_forecasted_id.setu_advance_budget_forecasted_periods_ids:
                    setu_advance_budget_forecasted_position_id = setu_advance_budget_forecasted_position_obj.create(
                        {"start_date": setu_advance_budget_forecasted_periods_id.start_date,
                         "end_date": setu_advance_budget_forecasted_periods_id.end_date,
                         "forecasted_type": setu_advance_budget_forecasted_periods_id.forecasted_type})
                    forecasted_position_lst.append(setu_advance_budget_forecasted_position_id.id)
                if forecasted_position_lst:
                    res['setu_advance_budget_forecasted_position_ids'] = [(6, 0, forecasted_position_lst)]
        return res

    planned_amount = fields.Float(string='Planned Amount', compute='_get_total_position_line_planned_amount',
                                  store=True)

    account_id = fields.Many2one(comodel_name='account.account', string='Account', required=False)
    setu_advance_budget_forecasted_sheet_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted.sheet',
                                                              string='Budget Forecasted Sheet', required=False)
    setu_advance_budget_forecasted_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted',
                                                        related="setu_advance_budget_forecasted_sheet_id.setu_advance_budget_forecasted_id",
                                                        string='Budget Forecast', required=False)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',
                                          related="setu_advance_budget_forecasted_sheet_id.analytic_account_id",
                                          string='Analytic Account', required=False)

    setu_advance_budget_forecasted_position_ids = fields.One2many(
        comodel_name='setu.advance.budget.forecasted.position',
        inverse_name='setu_advance_budget_forecasted_sheet_line_id', string='Budget Forecasted Position',
        required=False)

    @api.depends('setu_advance_budget_forecasted_position_ids')
    def _get_total_position_line_planned_amount(self):
        for forecasted_sheet_line_id in self:
            forecasted_sheet_line_id.planned_amount = sum(
                forecasted_sheet_line_id.setu_advance_budget_forecasted_position_ids.mapped('planned_amount'))

    @api.model
    def create(self, vals):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: set budget sheet record in budget position record
        """
        res = super(SetuAdvanceBudgetForeCastedSheetLine, self).create(vals)
        setu_advance_budget_forecasted_sheet_obj = self.env['setu.advance.budget.forecasted.sheet']

        if vals.get('setu_advance_budget_forecasted_sheet_id'):
            setu_advance_budget_forecasted_sheet_id = setu_advance_budget_forecasted_sheet_obj.browse(
                vals.get('setu_advance_budget_forecasted_sheet_id'))
            for forecasted_position_id in res.setu_advance_budget_forecasted_position_ids:
                forecasted_position_id.write({
                    "setu_advance_budget_forecasted_sheet_id": setu_advance_budget_forecasted_sheet_id and setu_advance_budget_forecasted_sheet_id.id})

        return res
