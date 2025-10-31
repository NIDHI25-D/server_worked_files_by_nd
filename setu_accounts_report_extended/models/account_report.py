from odoo import models, fields, api
from odoo.addons.web.controllers.utils import clean_action
from ast import literal_eval
from odoo.osv import expression


class AccountReport(models.Model):
    _inherit = 'account.report'

    report_line_id = fields.Many2one('account.report.line', 'Dividing Line')
    dividing_amount = fields.Char(string="Dividing number")
    filter_residual_amount = fields.Boolean(string="Residual Amount",
        compute=lambda x: x._compute_report_option_filter('filter_residual_amount'), readonly=False,
        store=True, depends=['root_report_id', 'section_main_report_ids'],
    )

    def get_options(self, previous_options):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18
            Purpose: to add a percentage in options of P&L.

            modified: to add residual_amount filter
            Task: customer statement missing column {https://app.clickup.com/t/86dxby19n} comment==> {https://app.clickup.com/t/86dxby19n?comment=90170148645183}

            Task: customer statement missing column { https://app.clickup.com/t/86dxby19n} comment==> https://app.clickup.com/t/86dxby19n?comment=90170149395014
            Purpose: if follow_up_email get in context, it will make residual_amount filter default true
        """
        res = super(AccountReport, self).get_options(previous_options)

        if previous_options:
            if 'percentage' in previous_options.keys():
                res['percentage'] = previous_options['percentage']
            if 'month13' in previous_options.keys():
                res['month13'] = previous_options['month13']

        if 'percentage' not in res.keys():
            res['percentage'] = True
        if 'month13' not in res.keys():
            res['month13'] = True
        if self.filter_residual_amount:
            if self._context.get('follow_up_email'):
                res['residual_amount'] = previous_options.get('residual_amount', True) if previous_options else True
            else:
                res['residual_amount'] = previous_options.get('residual_amount', False) if previous_options else False
        dividing_line_id = self.report_line_id

        if self.id == self.env.ref('account_reports.profit_and_loss').id \
                and dividing_line_id and res.get('percentage'):
            columns = res.get('columns')
            for column in range(len(columns)):
                column_group_key = \
                    [main_column.get('column_group_key') for
                     index, main_column in enumerate(columns, start=0) if
                     index >= column and main_column.get('expression_label') == 'balance']
                columns.insert(2 * column + 1, {'name': '%', 'expression_label': 'percentage',
                                                'figure_type': 'percentage', 'blank_if_zero': False,
                                                'sequence': 2,
                                                'column_group_key': column_group_key[0]})

        if self._context.get('partner_follow_up', False) and res.get('forced_domain', False):
            res['forced_domain'] += [('blocked', '!=', True)]

        return res

    @api.model
    def _create_hierarchy(self, lines, options):
        for col in [column for line in lines for column
                    in line.get('columns') if not column.get('no_format')]:
            col.update({'no_format': 0.0})
        res = super(AccountReport, self)._create_hierarchy(lines, options)
        return res

    def _fully_unfold_lines_if_needed(self, lines, options):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18
            Purpose: divide each line of profit and loss report
                     by report_line_id mentioned in the profit and
                     loss report
        """
        lines = \
            super(AccountReport, self)._fully_unfold_lines_if_needed(lines=lines, options=options)
        dividing_line_id = self.report_line_id
        if self.id == self.env.ref('account_reports.profit_and_loss').id and \
                dividing_line_id and options.get('percentage'):
            amounts_to_divide = [column.get('no_format') for
                                 line in lines if line.get('groupby') for column in
                                 line.get('columns') if
                                 column.get('report_line_id') == dividing_line_id.id and column.get(
                                     'expression_label') == 'balance']
            if amounts_to_divide:
                self.dividing_amount = amounts_to_divide
            for line in lines:
                amounts_to_divide = literal_eval(self.dividing_amount)
                column_to_divide = [column for column in line.get('columns') if
                                    column.get('expression_label') == 'balance']
                percentage_column_to_divide = [column for column in line.get('columns') if
                                               column.get('expression_label') == 'percentage']
                # if line.get('groupby') or line.get('caret_options'):
                for index, column in enumerate(column_to_divide, start=0):
                    percentage_column_to_write = percentage_column_to_divide[index]
                    amount_to_divide = amounts_to_divide[index]
                    if column.get('no_format'):
                        percentage = round((column.get('no_format') * 100 / amount_to_divide),
                                           2) if amount_to_divide > 0 else 0.0
                        percentage_column_to_write.update(
                            {'name': f"{percentage}%", 'no_format': percentage})
        return lines

    def _get_options_domain(self, options, date_scope):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18 Accounting - profit and loss filter issue
            Purpose: add custom filter as in version 14 due not configuration in version 16

            modified: add domain for residual_amount filter
            Task: customer statement missing column {https://app.clickup.com/t/86dxby19n} comment==> {https://app.clickup.com/t/86dxby19n?comment=90170148645183}
        """
        self.ensure_one()
        domain = super()._get_options_domain(options, date_scope)
        if self.id == self.env.ref('account_reports.profit_and_loss').id:
            if options.get('month13'):
                domain += self._get_options_month13_domain(options)

        if options.get('residual_amount'):
            domain += [('amount_residual', '!=',0.00),('account_type','=','asset_receivable'),('reconciled', '=', False)]
        return domain

    @api.model
    def _get_options_month13_domain(self, options):
        if options.get('month13'):
            return [('journal_id', '!=', 304)]

    def open_journal_items_profit_and_loss_report(self, options, params):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18 MVSA - Profit and Loss add Journal Items
            Purpose: journal item menu in profit and loss report for each account
        """
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_line_select")
        action = clean_action(action, env=self.env)
        ctx = self.env.context.copy()
        if params and 'line_id' in params:
            active_id = literal_eval(params.get('line_id').split('~')[-1])
            ctx.update({
                'active_id': active_id,
                'search_default_account_id': [active_id],
            })

        if options:
            domain = expression.normalize_domain(literal_eval(action.get('domain') or '[]'))
            if options.get('journals'):
                selected_journals = [journal['id'] for journal in options['journals'] if journal.get('selected')]
                if len(selected_journals) == 1:
                    ctx['search_default_journal_id'] = selected_journals
                elif selected_journals:  # Otherwise, nothing is selected, so we want to display everything
                    domain = expression.AND([domain, [('journal_id', 'in', selected_journals)]])

            analytic_account_ids = options.get('analytic_accounts_groupby')
            analytic_plans = options.get('analytic_plans_groupby')
            analytic_line_ids = False
            if analytic_account_ids or analytic_plans:
                all_plan_analytic_account_ids = False
                if analytic_plans:
                    analytic_plans_ids = self.env['account.analytic.plan'].search(
                        [('id', 'in', analytic_plans)])
                    all_plan_analytic_account_ids = analytic_account_ids + analytic_plans_ids.account_ids.ids
                analytic_line_ids = self.env['account.analytic.line'].search(
                    [('account_id', 'in',
                      (all_plan_analytic_account_ids if all_plan_analytic_account_ids else analytic_account_ids))])
            if analytic_line_ids:
                domain.append(('analytic_line_ids', 'in', analytic_line_ids.ids))
            if options.get('date'):
                opt_date = options['date']
                domain = expression.AND([domain, self._get_options_date_domain(options, 'strict_range')])

            if not options.get('all_entries'):
                ctx['search_default_posted'] = True

            action['domain'] = domain
        action['context'] = ctx
        return action
