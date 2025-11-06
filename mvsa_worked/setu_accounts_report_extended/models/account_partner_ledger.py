from odoo import fields, models, api, _
from collections import defaultdict
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
from odoo.tools import SQL


class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _build_partner_lines(self, report, options, level_shift=0):
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """
        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._build_partner_lines(report, options,level_shift)
        lines = []

        totals_by_column_group = {
            column_group_key: {
                total: 0.0
                for total in ['debit', 'credit', 'amount', 'balance','amount_residual']
            }
            for column_group_key in options['column_groups']
        }

        partners_results = self._query_partners(report, options)

        search_filter = options.get('filter_search_bar', '')
        accept_unknown_in_filter = search_filter.lower() in self._get_no_partner_line_label().lower()
        for partner, results in partners_results:
            if options['export_mode'] == 'print' and search_filter and not partner and not accept_unknown_in_filter:
                # When printing and searching for a specific partner, make it so we only show its lines, not the 'Unknown Partner' one, that would be
                # shown in case a misc entry with no partner was reconciled with one of the target partner's entries.
                continue

            partner_values = defaultdict(dict)
            for column_group_key in options['column_groups']:
                partner_sum = results.get(column_group_key, {})

                partner_values[column_group_key]['debit'] = partner_sum.get('debit', 0.0)
                partner_values[column_group_key]['credit'] = partner_sum.get('credit', 0.0)
                partner_values[column_group_key]['amount'] = partner_sum.get('amount', 0.0)
                partner_values[column_group_key]['balance'] = partner_sum.get('balance', 0.0)
                partner_values[column_group_key]['amount_residual'] = partner_sum.get('amount_residual', 0.0)

                totals_by_column_group[column_group_key]['debit'] += partner_values[column_group_key]['debit']
                totals_by_column_group[column_group_key]['credit'] += partner_values[column_group_key]['credit']
                totals_by_column_group[column_group_key]['amount'] += partner_values[column_group_key]['amount']
                totals_by_column_group[column_group_key]['balance'] += partner_values[column_group_key]['balance']
                totals_by_column_group[column_group_key]['amount_residual'] += partner_values[column_group_key]['amount_residual']

            lines.append(self._get_report_line_partners(options, partner, partner_values, level_shift=level_shift))

        return lines, totals_by_column_group

    def _query_partners(self, report, options):
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """

        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._query_partners(report,options)

        def assign_sum(row):
            if not self.env.context.get('customer_statement_report'):
                return super().assign_sum(row)
            fields_to_assign = ['balance', 'debit', 'credit', 'amount', 'amount_residual']
            if any(not company_currency.is_zero(row[field]) for field in fields_to_assign):
                groupby_partners.setdefault(row['groupby'], defaultdict(lambda: defaultdict(float)))
                for field in fields_to_assign:
                    groupby_partners[row['groupby']][row['column_group_key']][field] += row[field]

        company_currency = self.env.company.currency_id

        # Execute the queries and dispatch the results.
        query = self._get_query_sums(report, options)

        groupby_partners = {}

        self._cr.execute(query)
        for res in self._cr.dictfetchall():
            assign_sum(res)

        # Correct the sums per partner, for the lines without partner reconciled with a line having a partner
        query = self._get_sums_without_partner(options)

        self._cr.execute(query)
        totals = {}
        for total_field in ['debit', 'credit', 'amount', 'balance', 'amount_residual']:
            totals[total_field] = {col_group_key: 0 for col_group_key in options['column_groups']}

        for row in self._cr.dictfetchall():
            totals['debit'][row['column_group_key']] += row['debit']
            totals['credit'][row['column_group_key']] += row['credit']
            totals['amount'][row['column_group_key']] += row['amount']
            totals['balance'][row['column_group_key']] += row['balance']
            totals['amount_residual'][row['column_group_key']] += row['amount_residual']

            if row['groupby'] not in groupby_partners:
                continue

            assign_sum(row)

        if None in groupby_partners:
            # Debit/credit are inverted for the unknown partner as the computation is made regarding the balance of the known partner
            for column_group_key in options['column_groups']:
                groupby_partners[None][column_group_key]['debit'] += totals['credit'][column_group_key]
                groupby_partners[None][column_group_key]['credit'] += totals['debit'][column_group_key]
                groupby_partners[None][column_group_key]['amount'] += totals['amount'][column_group_key]
                groupby_partners[None][column_group_key]['balance'] -= totals['balance'][column_group_key]
                groupby_partners[None][column_group_key]['amount_residual'] += \
                totals['amount_residual'][column_group_key]

        # Retrieve the partners to browse.
        # groupby_partners.keys() contains all account ids affected by:
        # - the amls in the current period.
        # - the amls affecting the initial balance.
        if groupby_partners:
            # Note a search is done instead of a browse to preserve the table ordering.
            partners = self.env['res.partner'].with_context(active_test=False).search_fetch(
                [('id', 'in', list(groupby_partners.keys()))], ["id", "name", "trust", "company_registry", "vat"])
        else:
            partners = []

        # Add 'Partner Unknown' if needed
        if None in groupby_partners.keys():
            partners = [p for p in partners] + [None]

        return [(partner, groupby_partners[partner.id if partner else None]) for partner in partners]

    def _get_query_sums(self, report, options) -> SQL:
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """
        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._get_query_sums(report,options)

        queries = []

        # Create the currency table.
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(column_group_options, 'from_beginning')
            date_from = options['date']['date_from']
            queries.append(SQL(
                """
                (WITH partner_sums AS (
                    SELECT
                        account_move_line.partner_id            AS groupby,
                        %(column_group_key)s                    AS column_group_key,
                        SUM(%(debit_select)s)                   AS debit,
                        SUM(%(credit_select)s)                  AS credit,
                        SUM(%(balance_select)s)                 AS amount,
                        SUM(%(balance_select)s)                 AS balance,
                        SUM(CASE 
                            WHEN account_type = 'asset_receivable' AND account_move_line.reconciled = FALSE
                            THEN %(amount_residual_select)s 
                            ELSE 0 
                        END) AS amount_residual,
                        BOOL_AND(account_move_line.reconciled)  AS all_reconciled,
                        MAX(account_move_line.date)             AS latest_date
                    FROM %(table_references)s
                    %(currency_table_join)s
                    WHERE %(search_condition)s
                    GROUP BY account_move_line.partner_id
                )
                SELECT *
                FROM partner_sums
                WHERE partner_sums.balance != 0
                OR partner_sums.all_reconciled = FALSE
                OR partner_sums.latest_date >= %(date_from)s
                )""",
                column_group_key=column_group_key,
                debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                amount_residual_select=report._currency_table_apply_rate(
                    SQL("account_move_line.amount_residual")),
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(column_group_options),
                search_condition=query.where_clause,
                date_from=date_from,
            ))

        return SQL(' UNION ALL ').join(queries)

    def _get_initial_balance_values(self, partner_ids, options):
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """
        report_id = self.env['account.report'].search([('id', '=', options.get('report_id'))])
        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report_id:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._get_initial_balance_values(partner_ids,options)
        queries = []
        report = self.env.ref('account_reports.partner_ledger_report')
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            # Get sums for the initial balance.
            # period: [('date' <= options['date_from'] - 1)]
            new_options = self._get_options_initial_balance(column_group_options)
            query = report._get_report_query(new_options, 'from_beginning', domain=[('partner_id', 'in', partner_ids)])
            queries.append(SQL(
                """
                SELECT
                    account_move_line.partner_id,
                    %(column_group_key)s          AS column_group_key,
                    SUM(%(debit_select)s)         AS debit,
                    SUM(%(credit_select)s)        AS credit,
                    SUM(%(balance_select)s)       AS amount,
                    SUM(%(balance_select)s)       AS balance,
                    SUM(CASE 
                            WHEN account_type = 'asset_receivable' AND account_move_line.reconciled = FALSE
                            THEN %(amount_residual_select)s 
                            ELSE 0 
                        END) AS amount_residual
                FROM %(table_references)s
                %(currency_table_join)s
                WHERE %(search_condition)s
                GROUP BY account_move_line.partner_id
                """,
                column_group_key=column_group_key,
                debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                amount_residual_select=report._currency_table_apply_rate(SQL("account_move_line.amount_residual")),
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(column_group_options),
                search_condition=query.where_clause,
            ))

        self._cr.execute(SQL(" UNION ALL ").join(queries))

        init_balance_by_col_group = {
            partner_id: {column_group_key: {} for column_group_key in options['column_groups']}
            for partner_id in partner_ids
        }
        for result in self._cr.dictfetchall():
            init_balance_by_col_group[result['partner_id']][result['column_group_key']] = result

        return init_balance_by_col_group

    def _get_sums_without_partner(self, options):
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """
        report_id = self.env['account.report'].search([('id', '=', options.get('report_id'))])
        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report_id:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._get_sums_without_partner(options)

        queries = []
        report = self.env.ref('account_reports.partner_ledger_report')
        for column_group_key, column_group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(column_group_options, 'from_beginning')
            queries.append(SQL(
                """
                SELECT
                    %(column_group_key)s        AS column_group_key,
                    aml_with_partner.partner_id AS groupby,
                    SUM(%(debit_select)s)       AS debit,
                    SUM(%(credit_select)s)      AS credit,
                    SUM(%(balance_select)s)     AS amount,
                    SUM(%(balance_select)s)     AS balance,
                    SUM(CASE 
                            WHEN account_type = 'asset_receivable' AND account_move_line.reconciled = FALSE 
                            THEN %(amount_residual_select)s 
                            ELSE 0 
                        END) AS amount_residual
                FROM %(table_references)s
                JOIN account_partial_reconcile partial
                    ON account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id
                JOIN account_move_line aml_with_partner ON
                    (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                    AND aml_with_partner.partner_id IS NOT NULL
                %(currency_table_join)s
                WHERE partial.max_date <= %(date_to)s AND %(search_condition)s
                    AND account_move_line.partner_id IS NULL
                GROUP BY aml_with_partner.partner_id
                """,
                column_group_key=column_group_key,
                debit_select=report._currency_table_apply_rate(
                    SQL("CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE partial.amount END")),
                credit_select=report._currency_table_apply_rate(
                    SQL("CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE partial.amount END")),
                balance_select=report._currency_table_apply_rate(
                    SQL("-SIGN(aml_with_partner.balance) * partial.amount")),
                amount_residual_select=report._currency_table_apply_rate(
                    SQL("aml_with_partner.amount_residual")),
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(column_group_options,
                                                                    aml_alias=SQL("aml_with_partner")),
                date_to=column_group_options['date']['date_to'],
                search_condition=query.where_clause,
            ))

        return SQL(" UNION ALL ").join(queries)

    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        """
            Author: nidhi@setconsulting.com | Date: 16/09/25 |
            Task No: customer statement missing column {https://app.clickup.com/t/86dxby19n}
            Purpose: override method to add amount_residual
        """
        report_id = self.env['account.report'].search([('id', '=', options.get('report_id'))])
        custom_report_id = self.env.ref('account_reports.customer_statement_report')
        if custom_report_id == report_id:
            self = self.with_context(customer_statement_report=True)
        if not self.env.context.get('customer_statement_report'):
            return super(PartnerLedgerCustomHandler, self)._get_aml_values(options,partner_ids,offset, limit)
        rslt = {partner_id: [] for partner_id in partner_ids}

        partner_ids_wo_none = [x for x in partner_ids if x]
        directly_linked_aml_partner_clauses = []
        indirectly_linked_aml_partner_clause = SQL('aml_with_partner.partner_id IS NOT NULL')
        if None in partner_ids:
            directly_linked_aml_partner_clauses.append(SQL('account_move_line.partner_id IS NULL'))
        if partner_ids_wo_none:
            directly_linked_aml_partner_clauses.append(SQL('account_move_line.partner_id IN %s', tuple(partner_ids_wo_none)))
            indirectly_linked_aml_partner_clause = SQL('aml_with_partner.partner_id IN %s', tuple(partner_ids_wo_none))
        directly_linked_aml_partner_clause = SQL('(%s)', SQL(' OR ').join(directly_linked_aml_partner_clauses))

        queries = []
        journal_name = self.env['account.journal']._field_to_sql('journal', 'name')
        report = self.env.ref('account_reports.partner_ledger_report')
        additional_columns = self._get_additional_column_aml_values()
        order_by = self._get_order_by_aml_values()
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(group_options, 'strict_range')
            account_alias = query.left_join(lhs_alias='account_move_line', lhs_column='account_id', rhs_table='account_account', rhs_column='id', link='account_id')
            account_code = self.env['account.account']._field_to_sql(account_alias, 'code', query)
            account_name = self.env['account.account']._field_to_sql(account_alias, 'name')

            # For the move lines directly linked to this partner
            # ruff: noqa: FURB113
            queries.append(SQL(
                '''
                SELECT
                    account_move_line.id,
                    COALESCE(account_move_line.date_maturity, account_move_line.date) AS date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    %(additional_columns)s
                    COALESCE(account_move_line.invoice_date, account_move_line.date) AS invoice_date,
                    %(debit_select)s                                                 AS debit,
                    %(credit_select)s                                                AS credit,
                    %(balance_select)s                                               AS amount,
                    %(balance_select)s                                               AS balance,
                    CASE 
                            WHEN account_type = 'asset_receivable' AND account_move_line.reconciled = FALSE 
                            THEN %(amount_residual_select)s 
                            ELSE 0 
                        END                                             AS amount_residual,
                    account_move.name                                                AS move_name,
                    account_move.move_type                                           AS move_type,
                    %(account_code)s                                                 AS account_code,
                    %(account_name)s                                                 AS account_name,
                    journal.code                                                     AS journal_code,
                    %(journal_name)s                                                 AS journal_name,
                    %(column_group_key)s                                             AS column_group_key,
                    'directly_linked_aml'                                            AS key,
                    0                                                                AS partial_id
                FROM %(table_references)s
                JOIN account_move ON account_move.id = account_move_line.move_id
                %(currency_table_join)s
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                WHERE %(search_condition)s AND %(directly_linked_aml_partner_clause)s
                ORDER BY %(order_by)s
                ''',
                additional_columns=additional_columns,
                debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
                credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
                balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
                amount_residual_select=report._currency_table_apply_rate(SQL("account_move_line.amount_residual")),
                account_code=account_code,
                account_name=account_name,
                journal_name=journal_name,
                column_group_key=column_group_key,
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(group_options),
                search_condition=query.where_clause,
                directly_linked_aml_partner_clause=directly_linked_aml_partner_clause,
                order_by=order_by,
            ))

            # For the move lines linked to no partner, but reconciled with this partner. They will appear in grey in the report
            queries.append(SQL(
                '''
                SELECT
                    account_move_line.id,
                    COALESCE(account_move_line.date_maturity, account_move_line.date) AS date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    aml_with_partner.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    %(additional_columns)s
                    COALESCE(account_move_line.invoice_date, account_move_line.date) AS invoice_date,
                    %(debit_select)s                                                 AS debit,
                    %(credit_select)s                                                AS credit,
                    %(balance_select)s                                               AS amount,
                    %(balance_select)s                                               AS balance,
                    CASE 
                            WHEN account_type = 'asset_receivable' AND account_move_line.reconciled = FALSE 
                            THEN %(amount_residual_select)s 
                            ELSE 0 
                        END                          AS amount_residual,
                    account_move.name                                                AS move_name,
                    account_move.move_type                                           AS move_type,
                    %(account_code)s                                                 AS account_code,
                    %(account_name)s                                                 AS account_name,
                    journal.code                                                     AS journal_code,
                    %(journal_name)s                                                 AS journal_name,
                    %(column_group_key)s                                             AS column_group_key,
                    'indirectly_linked_aml'                                          AS key,
                    partial.id                                                       AS partial_id
                FROM %(table_references)s
                    %(currency_table_join)s,
                    account_partial_reconcile partial,
                    account_move,
                    account_move_line aml_with_partner,
                    account_journal journal
                WHERE
                    (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
                    AND account_move_line.partner_id IS NULL
                    AND account_move.id = account_move_line.move_id
                    AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                    AND %(indirectly_linked_aml_partner_clause)s
                    AND journal.id = account_move_line.journal_id
                    AND %(account_alias)s.id = account_move_line.account_id
                    AND %(search_condition)s
                    AND partial.max_date BETWEEN %(date_from)s AND %(date_to)s
                ORDER BY %(order_by)s
                ''',
                additional_columns=additional_columns,
                debit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE partial.amount END")),
                credit_select=report._currency_table_apply_rate(SQL("CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE partial.amount END")),
                balance_select=report._currency_table_apply_rate(SQL("-SIGN(aml_with_partner.balance) * partial.amount")),
                amount_residual_select=report._currency_table_apply_rate(SQL("aml_with_partner.amount_residual")),
                account_code=account_code,
                account_name=account_name,
                journal_name=journal_name,
                column_group_key=column_group_key,
                table_references=query.from_clause,
                currency_table_join=report._currency_table_aml_join(group_options),
                indirectly_linked_aml_partner_clause=indirectly_linked_aml_partner_clause,
                account_alias=SQL.identifier(account_alias),
                search_condition=query.where_clause,
                date_from=group_options['date']['date_from'],
                date_to=group_options['date']['date_to'],
                order_by=order_by,
            ))

        query = SQL(" UNION ALL ").join(SQL("(%s)", query) for query in queries)

        if offset:
            query = SQL('%s OFFSET %s ', query, offset)

        if limit:
            query = SQL('%s LIMIT %s ', query, limit)

        self._cr.execute(query)
        for aml_result in self._cr.dictfetchall():
            if aml_result['key'] == 'indirectly_linked_aml':

                # Append the line to the partner found through the reconciliation.
                if aml_result['partner_id'] in rslt:
                    rslt[aml_result['partner_id']].append(aml_result)

                # Balance it with an additional line in the Unknown Partner section but having reversed amounts.
                if None in rslt:
                    rslt[None].append({
                        **aml_result,
                        'debit': aml_result['credit'],
                        'credit': aml_result['debit'],
                        'amount': aml_result['credit'] - aml_result['debit'],
                        'balance': -aml_result['balance'],
                        'amount_residual': aml_result['amount_residual'],
                    })
            else:
                rslt[aml_result['partner_id']].append(aml_result)

        return rslt

