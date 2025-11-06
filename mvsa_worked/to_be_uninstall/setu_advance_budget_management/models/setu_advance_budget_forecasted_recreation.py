from odoo import fields, models, api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime


class SetuAdvanceBudgetForecastedRecreation(models.Model):
    _name = 'setu.advance.budget.forecasted.recreation'
    _description = 'Recreation Budget'

    @api.model
    def default_get(self, fields):
        res = super(SetuAdvanceBudgetForecastedRecreation, self).default_get(fields)
        setu_advance_budget_forecasted_obj = self.env['setu.advance.budget.forecasted']
        setu_advance_budget_forecasted_recreation_periods_obj = self.env[
            'setu.advance.budget.forecasted.recreation.periods']

        active_ids = self._context.get("active_ids", [])
        setu_advance_budget_forecasted_id = setu_advance_budget_forecasted_obj.browse(active_ids)

        if setu_advance_budget_forecasted_id:
            forecasted_recreation_periods_lst = []
            for setu_advance_budget_forecasted_periods_id in setu_advance_budget_forecasted_id.setu_advance_budget_forecasted_periods_ids:
                setu_advance_budget_forecasted_recreation_periods_id = setu_advance_budget_forecasted_recreation_periods_obj.create(
                    {"start_date": setu_advance_budget_forecasted_periods_id.start_date,
                     "end_date": setu_advance_budget_forecasted_periods_id.end_date,
                     "forecasted_type": setu_advance_budget_forecasted_periods_id.forecasted_type})

                forecasted_recreation_periods_lst.append(setu_advance_budget_forecasted_recreation_periods_id.id)
            if forecasted_recreation_periods_lst:
                res['setu_advance_budget_forecasted_recreation_periods_ids'] = [
                    (6, 0, forecasted_recreation_periods_lst)]

            res['setu_advance_budget_forecasted_id'] = setu_advance_budget_forecasted_id
            res['setu_advance_budget_forecasted_type_id'] = setu_advance_budget_forecasted_id.setu_advance_budget_forecasted_type_id
        return res

    is_old_budget_recreation = fields.Boolean(string="Is Old Budget To Recreation")
    is_create_new_periods = fields.Boolean(string="Create New Periods", default=False)

    name = fields.Char(string="New Budget Name")

    update_budget_periods_count = fields.Integer(string='Add Count of the Budget Periods', placeholder="1,2,3...")

    recreation_budget_forecasted_period_type = fields.Selection(string='Recreation Budget Type', selection=[
        ('actual', 'Actual Amount copied into planned amount'), ('planned', 'Planned amount is set zero')],
                                                                required=False, default='actual')

    setu_advance_budget_forecasted_id = fields.Many2one(comodel_name='setu.advance.budget.forecasted', string='Budget')
    setu_advance_budget_forecasted_type_id = fields.Many2one('setu.advance.budget.forecasted.type', string="Type")

    setu_advance_budget_forecasted_recreation_periods_ids = fields.One2many(
        comodel_name='setu.advance.budget.forecasted.recreation.periods',
        inverse_name='setu_advance_budget_forecasted_recreation_id', string='Recreation Budget Periods', required=False)

    @api.onchange('is_create_new_periods')
    def _onchange_create_new_periods(self):
        if not self.is_create_new_periods:
            self.update_budget_periods_count = 0

    def prepare_and_create_new_budget_plan(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: button(in recreation of budget wizard) to create new budget
        """
        setu_advance_budget_forecasted_obj = self.env['setu.advance.budget.forecasted']
        setu_advance_budget_forecasted_sheet_obj = self.env['setu.advance.budget.forecasted.sheet']
        setu_advance_budget_forecasted_sheet_line_obj = self.env['setu.advance.budget.forecasted.sheet.line']
        setu_advance_budget_forecasted_periods_obj = self.env['setu.advance.budget.forecasted.periods']
        setu_advance_budget_forecasted_position_obj = self.env['setu.advance.budget.forecasted.position']

        budget_forecasted_id = self.setu_advance_budget_forecasted_id

        recreation_budget_id = setu_advance_budget_forecasted_obj.create(
            {"name": self.name, "date_from": budget_forecasted_id.date_from, "date_to": budget_forecasted_id.date_to,
             "setu_advance_budget_forecasted_type_id": self.setu_advance_budget_forecasted_type_id and self.setu_advance_budget_forecasted_type_id.id})
        if self.is_old_budget_recreation:
            recreation_budget_id.write(
                {"current_budget_forecasted_id": budget_forecasted_id and budget_forecasted_id.id})

        self._onchange_update_count_periods()
        for setu_advance_budget_forecasted_recreation_period_id in self.setu_advance_budget_forecasted_recreation_periods_ids:
            setu_advance_budget_forecasted_periods_obj.create(
                {"start_date": setu_advance_budget_forecasted_recreation_period_id.start_date,
                 "end_date": setu_advance_budget_forecasted_recreation_period_id.end_date,
                 "forecasted_type": setu_advance_budget_forecasted_recreation_period_id.forecasted_type,
                 "setu_advance_budget_forecasted_id": recreation_budget_id and recreation_budget_id.id})

        for budget_forecasted_sheet_id in budget_forecasted_id.setu_advance_budget_forecasted_sheet_ids:
            recreation_budget_forecasted_sheet_id = setu_advance_budget_forecasted_sheet_obj.create(
                {"analytic_account_id": budget_forecasted_sheet_id.analytic_account_id.id,
                 "setu_advance_budget_forecasted_id": recreation_budget_id and recreation_budget_id.id})
            for setu_advance_budget_forecasted_sheet_line_id in budget_forecasted_sheet_id.setu_advance_budget_forecasted_sheet_line_ids:
                recreation_budget_forecasted_sheet_line_id = setu_advance_budget_forecasted_sheet_line_obj.create(
                    {"account_id": setu_advance_budget_forecasted_sheet_line_id.account_id.id,
                     "setu_advance_budget_forecasted_id": recreation_budget_id and recreation_budget_id.id,
                     "setu_advance_budget_forecasted_sheet_id": recreation_budget_forecasted_sheet_id and recreation_budget_forecasted_sheet_id.id})
                #
                # planned_amount = sum(
                #     setu_advance_budget_forecasted_sheet_line_id.setu_advance_budget_forecasted_position_ids.filtered(
                #         lambda x: x.forecasted_type == 'planned').mapped('planned_amount'))
                # total_orders_ids = len(
                #     setu_advance_budget_forecasted_sheet_line_id.setu_advance_budget_forecasted_position_ids.filtered(
                #         lambda x: x.forecasted_type == 'planned'))
                # actual_planned_amount = planned_amount / total_orders_ids
                for recreation_budget_forecasted_periods_id in recreation_budget_id.setu_advance_budget_forecasted_periods_ids:
                    old_planned_amount_record = setu_advance_budget_forecasted_sheet_line_id.setu_advance_budget_forecasted_position_ids.filtered(lambda month:month.start_date == recreation_budget_forecasted_periods_id.start_date and
                                                                                                                      month.end_date == recreation_budget_forecasted_periods_id.end_date)
                    old_planned_amount = sum(old_planned_amount_record.mapped('planned_amount'))
                    if recreation_budget_forecasted_periods_id.forecasted_type == 'planned':
                        setu_advance_budget_forecasted_position_obj.create(
                            {"start_date": recreation_budget_forecasted_periods_id.start_date,
                             "end_date": recreation_budget_forecasted_periods_id.end_date,
                             "forecasted_type": recreation_budget_forecasted_periods_id.forecasted_type,
                             "setu_advance_budget_forecasted_id": recreation_budget_id and recreation_budget_id.id,
                             "setu_advance_budget_forecasted_sheet_id": recreation_budget_forecasted_sheet_id and recreation_budget_forecasted_sheet_id.id,
                             "planned_amount": old_planned_amount ,
                             "setu_advance_budget_forecasted_sheet_line_id": recreation_budget_forecasted_sheet_line_id and recreation_budget_forecasted_sheet_line_id.id})

                    else:
                        move_lines = False
                        sheet_line_analytic_account_id = setu_advance_budget_forecasted_sheet_line_id.analytic_account_id
                        if sheet_line_analytic_account_id:
                            analytic_line_ids = self.env['account.analytic.line'].search(
                                [('account_id', '=', sheet_line_analytic_account_id.id)])
                            move_lines = self.env['account.move.line'].search_read(
                                domain=[('date', '>=', recreation_budget_forecasted_periods_id.start_date),
                                        ('date', '<=', recreation_budget_forecasted_periods_id.end_date),
                                        ('analytic_line_ids', 'in', analytic_line_ids.ids),
                                        (
                                        'account_id', '=', setu_advance_budget_forecasted_sheet_line_id.account_id.id)],
                                fields=['debit', 'credit'])
                        else:
                            move_lines = self.env['account.move.line'].search_read(
                                domain=[('date', '>=', recreation_budget_forecasted_periods_id.start_date),
                                        ('date', '<=', recreation_budget_forecasted_periods_id.end_date),
                                        ('account_id', '=', setu_advance_budget_forecasted_sheet_line_id.account_id.id)],
                                fields=['debit', 'credit'])
                        actual_amount_in_journal_items = sum(line.get('debit') for line in move_lines) - sum(
                            line.get('credit') for line in move_lines) if setu_advance_budget_forecasted_sheet_line_id.account_id.account_type not in ('income', 'other_income') else sum(line.get('credit') for line in move_lines) - sum(
                            line.get('debit') for line in move_lines)
                        setu_advance_budget_forecasted_position_obj.create(
                            {"start_date": recreation_budget_forecasted_periods_id.start_date,
                             "end_date": recreation_budget_forecasted_periods_id.end_date,
                             "forecasted_type": recreation_budget_forecasted_periods_id.forecasted_type,
                             "setu_advance_budget_forecasted_id": recreation_budget_id and recreation_budget_id.id,
                             "setu_advance_budget_forecasted_sheet_id": recreation_budget_forecasted_sheet_id and recreation_budget_forecasted_sheet_id.id,
                             "setu_advance_budget_forecasted_sheet_line_id": recreation_budget_forecasted_sheet_line_id and recreation_budget_forecasted_sheet_line_id.id,
                             "planned_amount": actual_amount_in_journal_items})

        recreation_budget_id.action_budget_confirm()
        start_date = self.setu_advance_budget_forecasted_recreation_periods_ids[0].start_date
        end_date = self.setu_advance_budget_forecasted_recreation_periods_ids[-1].end_date
        recreation_budget_id.write({"date_from": start_date, "date_to": end_date})
        return {'name': (_('%s'%recreation_budget_id.name)),
                'view_mode': 'form',
                'res_model': 'setu.advance.budget.forecasted',
                'res_id': recreation_budget_id.id,
                'view_id': False,
                'type': 'ir.actions.act_window', }


    @api.onchange('update_budget_periods_count')
    def _onchange_update_count_periods(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: update periods according to set period in recreation budget wizard
        """
        if self.update_budget_periods_count and self.update_budget_periods_count > 0:
            start_date = self.setu_advance_budget_forecasted_recreation_periods_ids[0].start_date + relativedelta(months=self.update_budget_periods_count * 12)
            end_date = self.setu_advance_budget_forecasted_recreation_periods_ids[-1].end_date + relativedelta(months=self.update_budget_periods_count * 12)
            ds = datetime.strptime(start_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
            for setu_advance_budget_forecasted_recreation_periods_id in self.setu_advance_budget_forecasted_recreation_periods_ids:
                de = ds + relativedelta(months=self.update_budget_periods_count, days=-1)
                if de.date() > end_date:
                    de = datetime.strptime(str(end_date),   '%Y-%m-%d') + relativedelta(months=self.update_budget_periods_count)
                setu_advance_budget_forecasted_recreation_periods_id.update({'start_date': ds.strftime('%Y-%m-%d'),'end_date': de.strftime('%Y-%m-%d')})
                ds += relativedelta(months=self.update_budget_periods_count)

