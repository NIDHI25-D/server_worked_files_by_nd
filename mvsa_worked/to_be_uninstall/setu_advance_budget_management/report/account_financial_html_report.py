
from odoo import models, fields, api, _

class ReportAccountFinancialReport(models.Model):
    _inherit = "account.report"

    setu_advance_budget_id = fields.Many2one('setu.advance.budget.forecasted', string="Budget")

    def _init_options_comparison(self, options, previous_options=None):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: return all done budget records
        """
        super()._init_options_comparison(options=options, previous_options=previous_options)
        setu_advance_budget_ids = self.env['setu.advance.budget.forecasted'].search([('state', '=', 'done')])
        options['budget_ids'] = setu_advance_budget_ids

    def get_report_informations(self, options):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: return selected budget id in profit and loss report
        """
        options = self._get_options(options)
        if options.get('comparison') and options.get('comparison').get('setu_advance_budget_id'):
            options['selected_budget_ids'] = [self.env['setu.advance.budget.forecasted'].browse(int(budget_id)).name for budget_id in options.get('comparison').get('setu_advance_budget_id')]
        return super().get_report_informations(options)