from odoo import models, _


class CustomerStatementCustomHandler(models.AbstractModel):
    _inherit = 'account.customer.statement.report.handler'

    def _custom_options_initializer(self, report, options, previous_options):
        """
            Author: nidhi@setconsulting.com
            Date: 24/08/25
            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose: to select particular jornal when cron 'Account Report Followup; Execute followup' execute. so that only record with journal
            sent to customer in mail
        """
        super()._custom_options_initializer(report, options, previous_options)

        if options['report_id'] != previous_options.get('report_id') and self._context.get('follow_up_email'):
            journal_ids = eval(self.env['ir.config_parameter'].sudo().get_param('setu_accounts_report_extended.selected_journal_ids'))
            for journal in options.get('journals', []):
                journal['selected'] = journal.get('id') in journal_ids
            # Since we forced the selection of some journal, we need to recompute the filter label
            report._init_options_journals_names(options, previous_options=previous_options)