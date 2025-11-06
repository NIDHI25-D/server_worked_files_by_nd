from odoo import models, fields, api, _
import json
import ast
from odoo.osv import expression
from odoo.addons.web.controllers.utils import clean_action
from datetime import datetime
from ast import literal_eval
from collections import defaultdict
from odoo.exceptions import ValidationError, UserError


class AccountReport(models.Model):
    _inherit = 'account.report'

    def _get_options(self, previous_options):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: add column of budget value , difference value and percentage in profit and loss report
        """
        res = super(AccountReport, self)._get_options(previous_options)
        if previous_options:
            comparison = previous_options.get('comparison')
            budget_id = (comparison and comparison.get('budget_id')) or previous_options.get('budget_id')
            percentage = res.get('percentage')
            res['budget_id'] = budget_id
            if self.id == self.env.ref('account_reports.profit_and_loss').id and budget_id:
                budget_record = self.env['setu.advance.budget.forecasted'].browse(budget_id)
                columns = res.get('columns')
                for column in range(len([col for col in columns if col.get('expression_label') == 'balance'])):
                    column_group_key = [main_column.get('column_group_key') for index, main_column in
                                        enumerate(columns, start=0) if
                                        index >= column and main_column.get('expression_label') == 'balance']
                    length_of_column = len(columns)
                    columns.insert(length_of_column, {'name': budget_record.name, 'expression_label': 'budget_number',
                                                      'figure_type': 'monetary', 'blank_if_zero': True,
                                                      'column_group_key': column_group_key[-1]})
                    columns.insert(length_of_column + 1,
                                   {'name': 'Diff.Abs.', 'expression_label': 'budget_difference_number',
                                    'figure_type': 'monetary', 'blank_if_zero': True,
                                    'column_group_key': column_group_key[-1]})
                    columns.insert(length_of_column + 2, {'name': 'Diff.%', 'expression_label': 'budget_percentage',
                                                          'figure_type': 'percentage', 'blank_if_zero': True,
                                                          'column_group_key': column_group_key[-1]})
                    break
        return res

    def _fully_unfold_lines_if_needed(self, lines, options):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: set value of budget related fields in the profit and loss report
        """
        lines = super(AccountReport, self)._fully_unfold_lines_if_needed(lines=lines, options=options)

        budget_id = options.get('budget_id')
        budget_record = self.env['setu.advance.budget.forecasted'].browse(budget_id)
        company_currency_id = self.env.company.currency_id
        income = ('income', 'income_other')
        if self.id == self.env.ref('account_reports.profit_and_loss').id and budget_id:
            final_line = {}
            start_date = []
            end_date = []
            analytic_account_ids = options.get('analytic_accounts_groupby')
            analytic_plans = options.get('analytic_plans_groupby')
            journals = options.get('journals')
            selected_journal = [journal.get('id') for journal in journals if journal.get('selected')]
            date_from = options.get('date').get('date_from')
            date_to = options.get('date').get('date_to')
            date_from_month = int(date_from.split('-')[1])
            date_to_month = int(date_to.split('-')[1])
            date_from_year = int(date_from.split('-')[0])
            date_to_year = int(date_to.split('-')[0])
            budget_record_dates = budget_record.setu_advance_budget_forecasted_periods_ids
            for date in budget_record_dates:
                if date.start_date.month == date_from_month:
                    start_date.append(date.start_date.strftime('%Y-%m-%d'))
                if date.end_date.month == date_to_month:
                    end_date.append(date.end_date.strftime('%Y-%m-%d'))
            account_ids = self.env["ir.default"].sudo().get('res.config.settings', 'account_ids',
                                                            company_id=self.env.company.id)
            acoount_ids_list = account_ids

            for line in lines:
                if line.get('groupby'):
                    if analytic_account_ids or analytic_plans:
                        all_plan_analytic_account_ids = False
                        if analytic_plans:
                            analytic_plans_ids = self.env['account.analytic.plan'].search(
                                [('id', 'in', analytic_plans)])
                            all_plan_analytic_account_ids = analytic_account_ids + analytic_plans_ids.account_ids.ids
                    analytic_line_ids = False
                    report_line_id = line.get('columns')[0].get('report_line_id')
                    type_of_account = \
                    literal_eval(self.env['account.report.line'].browse(report_line_id).expression_ids.formula)[0][2]
                    planned_amount = 0
                    difference_planned_amount = 0
                    sum_count = 0
                    # for sheet in budget_record.setu_advance_budget_forecasted_sheet_ids:
                    sheet_filtered_according_to_account = False
                    if analytic_account_ids or analytic_plans:
                        sheet_filtered_according_to_account = budget_record.setu_advance_budget_forecasted_sheet_ids.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                            lambda
                                account: account.account_id.account_type == type_of_account and account.analytic_account_id.id in (
                                all_plan_analytic_account_ids if all_plan_analytic_account_ids else analytic_account_ids))
                        analytic_line_ids = self.env['account.analytic.line'].search(
                            [('account_id', 'in', (
                                all_plan_analytic_account_ids if all_plan_analytic_account_ids else analytic_account_ids))])
                    else:
                        sheet_filtered_according_to_account = budget_record.setu_advance_budget_forecasted_sheet_ids.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                            lambda
                                account: account.account_id.account_type == type_of_account)

                    planned_amount += sum(
                        sheet_filtered_according_to_account.setu_advance_budget_forecasted_position_ids.filtered(
                            lambda date: date.start_date.strftime('%Y-%m-%d') >= start_date[
                                0] and date.end_date.strftime('%Y-%m-%d') <= end_date[0]).mapped('planned_amount'))
                    actual_amount = line.get('columns')[0].get('no_format')


                    if type_of_account in income:
                        difference_planned_amount = actual_amount - planned_amount
                    else:
                        difference_planned_amount = planned_amount - actual_amount

                    if line.get('name') not in final_line.keys():
                        final_line.__setitem__(line.get('name'),
                                               (actual_amount, planned_amount))
                    for column in line.get('columns'):
                        expression_label = column.get('expression_label')
                        if expression_label in ('budget_number', 'budget_difference_number', 'budget_percentage'):
                            rounded_planned_amount = round(planned_amount, 2)
                            rounded_difference_planned_amount = round(difference_planned_amount, 2)
                            if expression_label == 'budget_number':
                                column.update({
                                                  'name': f"{self.format_value(abs(rounded_planned_amount), figure_type='monetary')}",
                                                  'no_format': abs(rounded_planned_amount)})
                            elif expression_label == 'budget_difference_number':
                                class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                column.update({
                                                  'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                  'no_format': rounded_difference_planned_amount,
                                                  'class': class_color})
                            else:
                                class_color = ''
                                if rounded_planned_amount == 0.0 or rounded_difference_planned_amount == 0:
                                    class_color = ''
                                else:
                                    if round((rounded_difference_planned_amount / rounded_planned_amount) * 100, 2) > 0.0:
                                        class_color = 'number extra_foldable_line_green'
                                    else:
                                        class_color = 'number extra_foldable_line_red'
                                column.update({
                                                  'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / rounded_planned_amount) * 100, 2)}%",
                                                  'no_format': "N/A" if rounded_planned_amount == 0.0 else round((rounded_difference_planned_amount / rounded_planned_amount) * 100,2),
                                                  'class': class_color})
                if ('Operating Income' in final_line.keys() or 'Ingresos de operación' in final_line.keys()) and (
                        'Cost of Revenue' in final_line.keys() or 'Costo de ingresos' in final_line.keys()):
                    if 'Total Gross Profit' not in final_line.keys() or 'Total Ganancia bruta' not in final_line.keys():
                        income_line = [line for line in lines if
                                       line.get('name') in ('Total Gross Profit', 'Total Ganancia bruta')]
                        if income_line:
                            for incom_line in income_line:
                                operating_income_with_language = 'Ingresos de operación' if self.env.lang == 'es_MX' else 'Operating Income'
                                cost_of_revenue_with_language = 'Costo de ingresos' if self.env.lang == 'es_MX' else 'Cost of Revenue'
                                actual_amount = final_line.get(operating_income_with_language)[0] - \
                                                final_line.get(cost_of_revenue_with_language)[0]
                                total_planned_amount = final_line.get(operating_income_with_language)[1] - \
                                                       final_line.get(cost_of_revenue_with_language)[1]
                                difference_planned_amount = actual_amount - total_planned_amount
                                rounded_planned_amount = round(total_planned_amount, 2)
                                rounded_difference_planned_amount = round(difference_planned_amount,
                                                                          2)
                                for column in incom_line.get('columns'):
                                    expression_label = column.get('expression_label')
                                    if expression_label in (
                                    'budget_number', 'budget_difference_number', 'budget_percentage'):
                                        if expression_label == 'budget_number':
                                            column.update({
                                                              'name': f"{self.format_value(round(abs(final_line.get(operating_income_with_language)[1]) - abs(final_line.get(cost_of_revenue_with_language)[1]), 2), figure_type='monetary')}",
                                                              'no_format': round(abs(
                                                                  final_line.get(operating_income_with_language)[
                                                                      1]) - abs(
                                                                  final_line.get(cost_of_revenue_with_language)[1]),
                                                                                 2)})
                                        elif expression_label == 'budget_difference_number':
                                            class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                            column.update({
                                                              'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                              'no_format': rounded_difference_planned_amount,
                                                              'class': class_color})
                                        else:
                                            class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount != 0 and round(
                                                (rounded_difference_planned_amount / round(
                                                    abs(final_line.get(operating_income_with_language)[1]) - abs(
                                                        final_line.get(cost_of_revenue_with_language)[1]), 2)) * 100,
                                                2) > 0 else 'number extra_foldable_line_red'
                                            column.update({
                                                              'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / round(abs(final_line.get(operating_income_with_language)[1]) - abs(final_line.get(cost_of_revenue_with_language)[1]), 2)) * 100, 2)}%",
                                                              'no_format': "N/A" if rounded_planned_amount == 0.0 else round(
                                                                  (rounded_difference_planned_amount / round(abs(
                                                                      final_line.get(operating_income_with_language)[
                                                                          1]) - abs(
                                                                      final_line.get(cost_of_revenue_with_language)[1]),
                                                                                                             2)) * 100,
                                                                  2, ),
                                                              'class': class_color})

                                if incom_line.get('name') in final_line.keys():
                                    final_line.update(
                                        {f"{incom_line.get('name')}": (actual_amount, rounded_planned_amount)})
                                else:
                                    final_line.__setitem__(incom_line.get('name'),
                                                           (actual_amount, rounded_planned_amount))

                if ('Total Gross Profit' in final_line.keys() or 'Total Ganancia bruta' in final_line.keys()) and (
                        'Other Income' in final_line.keys() or 'Otros ingresos' in final_line.keys()):
                    if 'Total Income' not in final_line.keys() or 'Total Ingreso' not in final_line.keys():
                        income_line = [line for line in lines if line.get('name') in ('Total Income', 'Total Ingreso')]
                        if income_line:
                            for incom_line in income_line:
                                total_gross_profit_with_language = 'Total Ganancia bruta' if self.env.lang == 'es_MX' else 'Total Gross Profit'
                                other_income_with_language = 'Otros ingresos' if self.env.lang == 'es_MX' else 'Other Income'
                                actual_amount = final_line.get(total_gross_profit_with_language)[0] + \
                                                final_line.get(other_income_with_language)[0]
                                total_planned_amount = final_line.get(total_gross_profit_with_language)[1] + \
                                                       final_line.get(other_income_with_language)[1]
                                difference_planned_amount = actual_amount - total_planned_amount
                                rounded_planned_amount = round(total_planned_amount, 2)
                                rounded_difference_planned_amount = round(difference_planned_amount,
                                                                          2)
                                for column in incom_line.get('columns'):
                                    expression_label = column.get('expression_label')
                                    if expression_label in (
                                    'budget_number', 'budget_difference_number', 'budget_percentage'):
                                        if expression_label == 'budget_number':
                                            column.update({
                                                              'name': f"{self.format_value(round(abs(final_line.get(total_gross_profit_with_language)[1]) + abs(final_line.get(other_income_with_language)[1]), 2), figure_type='monetary')}",
                                                              'no_format': round(abs(
                                                                  final_line.get(total_gross_profit_with_language)[
                                                                      1]) + abs(
                                                                  final_line.get(other_income_with_language)[1]), 2)})
                                        elif expression_label == 'budget_difference_number':
                                            class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                            column.update({
                                                              'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                              'no_format': rounded_difference_planned_amount,
                                                              'class': class_color})
                                        else:
                                            class_color = 'number extra_foldable_line_green' if rounded_planned_amount != 0 and round(
                                                (rounded_difference_planned_amount / round(
                                                    abs(final_line.get(total_gross_profit_with_language)[1]) + abs(
                                                        final_line.get(other_income_with_language)[1]), 2)) * 100,
                                                2) > 0 else 'number extra_foldable_line_red'
                                            column.update({
                                                              'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / round(abs(final_line.get(total_gross_profit_with_language)[1]) + abs(final_line.get(other_income_with_language)[1]), 2)) * 100, 2)} % ",
                                                              'no_format': "N/A" if rounded_planned_amount == 0.0 else round(
                                                                  (rounded_difference_planned_amount / round(abs(
                                                                      final_line.get(total_gross_profit_with_language)[
                                                                          1]) + abs(
                                                                      final_line.get(other_income_with_language)[1]),
                                                                                                             2)) * 100,
                                                                  2),
                                                              'class': class_color})

                                if incom_line.get('name') in final_line.keys():
                                    final_line.update(
                                        {f"{incom_line.get('name')}": (actual_amount, rounded_planned_amount)})
                                else:
                                    final_line.__setitem__(incom_line.get('name'),
                                                           (actual_amount, rounded_planned_amount))
                if ('Expenses' in final_line.keys() or 'Gastos' in final_line.keys()) or (
                        'Depreciation' in final_line.keys() or 'Depreciación' in final_line.keys()):
                    # if 'Total Expenses' not in final_line.keys():
                    income_line = [line for line in lines if line.get('name') in ('Total Expenses', 'Total Gastos')]
                    if income_line:
                        for incom_line in income_line:
                            expense_with_language = 'Gastos' if self.env.lang == 'es_MX' else 'Expenses'
                            depreciation_with_language = 'Depreciación' if self.env.lang == 'es_MX' else 'Depreciation'
                            actual_amount = final_line.get(expense_with_language)[0] + \
                                            final_line.get(depreciation_with_language)[0] if final_line.get(
                                depreciation_with_language) else 0
                            total_planned_amount = final_line.get(expense_with_language)[1] + \
                                                   final_line.get(depreciation_with_language)[1] if final_line.get(
                                depreciation_with_language) else 0
                            difference_planned_amount = total_planned_amount - actual_amount
                            rounded_planned_amount = round(total_planned_amount, 2)
                            rounded_difference_planned_amount = round(difference_planned_amount,
                                                                      2)
                            for column in incom_line.get('columns'):
                                expression_label = column.get('expression_label')
                                if expression_label in (
                                'budget_number', 'budget_difference_number', 'budget_percentage'):
                                    if expression_label == 'budget_number':
                                        column.update({
                                                          'name': f"{self.format_value(round(abs(final_line.get(expense_with_language)[1]) + abs(final_line.get(depreciation_with_language)[0]) if final_line.get(depreciation_with_language) else 0, 2), figure_type='monetary')}",
                                                          'no_format': round(
                                                              abs(final_line.get(expense_with_language)[1]) + abs(
                                                                  final_line.get(depreciation_with_language)[
                                                                      0]) if final_line.get(
                                                                  depreciation_with_language) else 0, 2)})
                                    elif expression_label == 'budget_difference_number':
                                        class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                        column.update({
                                                          'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                          'no_format': rounded_difference_planned_amount,
                                                          'class': class_color})
                                    else:
                                        class_color = 'number extra_foldable_line_green' if rounded_planned_amount != 0 and round(
                                            (rounded_difference_planned_amount / round(
                                                abs(final_line.get(expense_with_language)[1]) + abs(
                                                    final_line.get(depreciation_with_language)[0]) if final_line.get(
                                                    depreciation_with_language) else 0, 2)) * 100,
                                            2) > 0 else 'number extra_foldable_line_red'
                                        column.update({
                                                          'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / round(abs(final_line.get(expense_with_language)[1]) + abs(final_line.get(depreciation_with_language)[0]) if final_line.get(depreciation_with_language) else 0, 2)) * 100, 2)}%",
                                                          'no_format': "N/A" if rounded_planned_amount == 0.0 else round(
                                                              (rounded_difference_planned_amount / round(
                                                                  abs(final_line.get(expense_with_language)[1]) + abs(
                                                                      final_line.get(depreciation_with_language)[
                                                                          0]) if final_line.get(
                                                                      depreciation_with_language) else 0, 2)) * 100, 2),
                                                          'class': class_color})

                            if incom_line.get('name') in final_line.keys():
                                final_line.update(
                                    {f"{incom_line.get('name')}": (actual_amount, rounded_planned_amount)})
                            else:
                                final_line.__setitem__(incom_line.get('name'),
                                                       (actual_amount, rounded_planned_amount))

                if ('Total Income' in final_line.keys() or 'Total Ingreso' in final_line.keys()) and (
                        'Total Expenses' in final_line.keys() or 'Total Gastos' in final_line.keys()):
                    # if 'Total Expenses' not in final_line.keys():
                    income_line = [line for line in lines if line.get('name') in ('Net Profit', 'Ganancias netas')]
                    if income_line:
                        for incom_line in income_line:
                            total_income_with_language = 'Total Ingreso' if self.env.lang == 'es_MX' else 'Total Income'
                            total_expense_with_language = 'Total Gastos' if self.env.lang == 'es_MX' else 'Total Expenses'
                            actual_amount = final_line.get(total_income_with_language)[0] - final_line.get(total_expense_with_language)[0]
                            total_planned_amount = final_line.get(total_income_with_language)[1] - \
                                                   final_line.get(total_expense_with_language)[1] if final_line.get(
                                total_expense_with_language) else 0
                            difference_planned_amount = actual_amount - total_planned_amount
                            rounded_planned_amount = round(total_planned_amount, 2)
                            rounded_difference_planned_amount = round(difference_planned_amount,
                                                                      2)
                            for column in incom_line.get('columns'):
                                expression_label = column.get('expression_label')
                                if expression_label in (
                                'budget_number', 'budget_difference_number', 'budget_percentage'):
                                    if expression_label == 'budget_number':

                                        column.update({'name': f"{self.format_value(round(abs(final_line.get(total_income_with_language)[1]) - abs(final_line.get(total_expense_with_language)[1]) if final_line.get(total_expense_with_language) else 0,2), figure_type='monetary')}",
                                                          'no_format': round(abs(final_line.get(total_income_with_language)[1]) - abs(final_line.get(total_expense_with_language)[1]) if final_line.get(total_expense_with_language) else 0,2)})
                                    elif expression_label == 'budget_difference_number':
                                        class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                        column.update({
                                                          'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                          'no_format': rounded_difference_planned_amount,
                                                          'class': class_color})
                                    else:
                                        class_color = 'number extra_foldable_line_green' if rounded_planned_amount != 0 and round(
                                            (rounded_difference_planned_amount / round(abs(final_line.get(total_income_with_language)[1]) - abs(final_line.get(total_expense_with_language)[1]) if final_line.get(
                                                total_expense_with_language) else 0,2)) * 100,
                                            2) > 0 else 'number extra_foldable_line_red'
                                        column.update({'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / round(abs(final_line.get(total_income_with_language)[1]) - abs(final_line.get(total_expense_with_language)[1]) if final_line.get(total_expense_with_language) else 0,2)) * 100, 2)}%",
                                                          'no_format': "N/A" if rounded_planned_amount == 0.0 else round((rounded_difference_planned_amount / round(abs(final_line.get(total_income_with_language)[1]) - abs(final_line.get(total_expense_with_language)[1]) if final_line.get(total_expense_with_language) else 0,2)) * 100,
                                                              2),
                                                          'class': class_color})

                if line.get('caret_options'):
                    if analytic_account_ids or analytic_plans:
                        all_plan_analytic_account_ids = False
                        if analytic_plans:
                            analytic_plans_ids = self.env['account.analytic.plan'].search(
                                [('id', 'in', analytic_plans)])
                            all_plan_analytic_account_ids = analytic_account_ids + analytic_plans_ids.account_ids.ids
                    analytic_line_ids = False
                    account_id = literal_eval(line.get('id').split('~')[-1])
                    account_record = self.env['account.account'].browse(account_id)
                    planned_amount = 0
                    difference_amount_of_individual_account = 0
                    for sheet in budget_record.setu_advance_budget_forecasted_sheet_ids:
                        sheet_filtered_according_to_account = False
                        if analytic_account_ids or analytic_plans:
                            sheet_filtered_according_to_account = sheet.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                                lambda
                                    account: account.account_id == account_record and account.analytic_account_id.id in (
                                    all_plan_analytic_account_ids if all_plan_analytic_account_ids else analytic_account_ids))
                            analytic_line_ids = self.env['account.analytic.line'].search(
                                [('account_id', 'in', (
                                    all_plan_analytic_account_ids if all_plan_analytic_account_ids else analytic_account_ids)),
                                 ('general_account_id', '=', account_record.id)])
                        else:
                            sheet_filtered_according_to_account = sheet.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                                lambda account: account.account_id == account_record)
                        planned_amount += sum(
                            sheet_filtered_according_to_account.setu_advance_budget_forecasted_position_ids.filtered(
                                lambda date: date.start_date.strftime('%Y-%m-%d') >= start_date[
                                    0] and date.end_date.strftime('%Y-%m-%d') <= end_date[0]).mapped(
                                'planned_amount'))
                    actual_amount = 0.0
                    domain = [('date', '>=', datetime.strptime(date_from, '%Y-%m-%d')),
                              ('date', '<=', datetime.strptime(date_to, '%Y-%m-%d')),
                              ('account_id', '=', account_record.id),
                              ('parent_state', '=', 'posted')]
                    if selected_journal:
                        domain.append(('move_id.journal_id', 'in', selected_journal))
                    if analytic_line_ids:
                        domain.append(('analytic_line_ids', 'in', analytic_line_ids.ids))
                    move_lines = self.env['account.move.line'].search_read(domain, fields=['debit', 'credit'])
                    if account_record.account_type in income:
                        amount_in_journal_items = sum(
                            line.get('credit') for line in move_lines) - sum(
                            line.get('debit') for line in move_lines)
                        difference_amount_of_individual_account += (amount_in_journal_items - planned_amount)
                    else:
                        amount_in_journal_items = sum(
                            line.get('debit') for line in move_lines) - sum(
                            line.get('credit') for line in move_lines)
                        difference_amount_of_individual_account += (planned_amount - amount_in_journal_items)
                    for column in line.get('columns'):
                        expression_label = column.get('expression_label')
                        if expression_label in ('budget_number', 'budget_difference_number', 'budget_percentage'):
                            rounded_planned_amount = round(planned_amount, 2)
                            rounded_difference_planned_amount = round(difference_amount_of_individual_account, 2)
                            if expression_label == 'budget_number':
                                column.update(
                                    {'name': f"{self.format_value(rounded_planned_amount, figure_type='monetary')}",
                                     'no_format': rounded_planned_amount})
                            elif expression_label == 'budget_difference_number':
                                class_color = 'number extra_foldable_line_green' if rounded_difference_planned_amount > 0 else 'number extra_foldable_line_red'
                                column.update({
                                                  'name': f"{self.format_value(rounded_difference_planned_amount, figure_type='monetary')}",
                                                  'no_format': rounded_difference_planned_amount,
                                                  'class': class_color})
                            else:
                                class_color = 'number extra_foldable_line_green' if rounded_planned_amount != 0 and round(
                                    (rounded_difference_planned_amount / rounded_planned_amount) * 100,
                                    2) > 0 else 'number extra_foldable_line_red'
                                column.update({
                                                  'name': "N/A" if rounded_planned_amount == 0.0 else f"{round((rounded_difference_planned_amount / rounded_planned_amount) * 100, 2)}%",
                                                  'no_format': "N/A" if rounded_planned_amount == 0.0 else round((rounded_difference_planned_amount / rounded_planned_amount) * 100,
                                                                                                                 2),
                                                  'class': class_color})

        return lines

    def _compute_formula_batch_with_engine_domain(self, options, date_scope, formulas_dict, current_groupby,
                                                  next_groupby, offset=0, limit=None):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: add accounts in profit and loss report if account have not move line for selected period
        """
        res = super(AccountReport, self)._compute_formula_batch_with_engine_domain(options, date_scope, formulas_dict,
                                                                                   current_groupby, next_groupby,
                                                                                   offset=offset, limit=limit)
        budget_id = options.get('budget_id')
        if self.id == self.env.ref('account_reports.profit_and_loss').id and budget_id:
            account_ids = self.env["ir.default"].sudo().get('res.config.settings', 'account_ids',
                                                            company_id=self.env.company.id)
            acoount_ids_list = account_ids
            for key, value in res.items():
                if type(value) == list:
                    specified_account_ids = self.env['account.account'].search(
                        [('id', 'in', account_ids), ('account_type', '=', literal_eval(key[0])[0][2])])
                    for account in specified_account_ids:
                        if account.id not in [account_id[0] for account_id in value]:
                            value.append((account.id, {'sum': 0, 'sum_if_pos': 0, 'sum_if_neg': 0, 'count_rows': 0,
                                                       'has_sublines': True}))
        return res

    def open_position_journal_items(self, options, params):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: add menuitem of journal entry to open that view from individual account in profit and loss report
        """
        if (options.get('comparison') and options.get('comparison').get('budget_id')) or options.get('budget_id'):
            action = self.env["ir.actions.actions"]._for_xml_id(
                "setu_advance_budget_management.setu_advance_budget_forecasted_position_action_open_for_specific_account_profit_and_loss_account")
            action = clean_action(action, env=self.env)
            analytic_account_ids_list = []
            if options.get('selected_analytic_account_names'):
                analytic_account_names = options.get('selected_analytic_account_names')
                for analytic_account_name in analytic_account_names:
                    analytic_account_ids = self.env['account.analytic.account'].search(
                        [('name', '=', analytic_account_name)])
                    analytic_account_ids_list.append(analytic_account_ids.id)
            budget_id = options.get('budget_id')
            start_date = []
            end_date = []
            date_from = options.get('date').get('date_from')
            date_to = options.get('date').get('date_to')
            date_from_month = int(date_from.split('-')[1])
            date_to_month = int(date_to.split('-')[1])
            budget_record = self.env['setu.advance.budget.forecasted'].browse(budget_id)
            budget_record_dates = budget_record.setu_advance_budget_forecasted_periods_ids
            for date in budget_record_dates:
                if date.start_date.month == date_from_month:
                    start_date.append(date.start_date.strftime('%Y-%m-%d'))
                if date.end_date.month == date_to_month:
                    end_date.append(date.end_date.strftime('%Y-%m-%d'))
            start_date = datetime.strptime(start_date[0], '%Y-%m-%d')
            end_date = datetime.strptime(end_date[0], '%Y-%m-%d')
            if params and 'id' in params:
                active_id = literal_eval(params.get('id').split('~')[-1])
                # active_id = self._get_caret_option_target_id(params['id'])
                domain = [('setu_advance_budget_forecasted_id', '=', budget_id), ('account_id', '=', active_id),
                          ('start_date', '>=', start_date.date()), ('end_date', '<=', end_date.date())]
                if options.get('selected_analytic_account_names'):
                    domain.append(('analytic_account_id', 'in', analytic_account_ids_list))
                action['domain'] = domain
            return action
        else:
            raise ValidationError(_('Please select budget to see budget positions.'))
