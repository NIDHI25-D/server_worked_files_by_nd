from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from ast import literal_eval


class SetuAdvanceBudgetForecasted(models.Model):
    _name = "setu.advance.budget.forecasted"
    _description = "Advance Budget"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, states={'done': [('readonly', True)]})

    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]})

    total_forecasted_sheet = fields.Integer(string='Sheet Records', compute='_get_total_count_forecasted_sheet')
    total_forecasted_sheet_line = fields.Integer(string='Sheet Line Records',
                                                 compute='_get_total_count_forecasted_line')
    total_forecasted_position = fields.Integer(string='Done Records', compute='_get_total_count_forecasted_position')
    number_of_reaction_budget = fields.Integer(string="Recreation Budget", compute='_get_no_reaction_budget')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)

    setu_advance_budget_forecasted_type_id = fields.Many2one('setu.advance.budget.forecasted.type', string="Type")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    current_budget_forecasted_id = fields.Many2one('setu.advance.budget.forecasted', string='Current revision',
                                                   readonly=True, copy=True)
    previous_budget_forecasted_ids = fields.One2many('setu.advance.budget.forecasted', 'current_budget_forecasted_id',
                                                     string='Previous Budget Forecast', readonly=True)

    setu_advance_budget_forecasted_periods_ids = fields.One2many(comodel_name='setu.advance.budget.forecasted.periods',
                                                                 inverse_name='setu_advance_budget_forecasted_id',
                                                                 string='Periods', required=False)
    setu_advance_budget_forecasted_sheet_ids = fields.One2many(comodel_name='setu.advance.budget.forecasted.sheet',
                                                               inverse_name='setu_advance_budget_forecasted_id',
                                                               string='Budget Forecasted Sheet', required=False)
    setu_advance_budget_forecasted_sheet_line_ids = fields.One2many(
        comodel_name='setu.advance.budget.forecasted.sheet.line', inverse_name='setu_advance_budget_forecasted_id',
        string='Budget Forecasted Sheet Line', required=False)
    setu_advance_budget_forecasted_position_ids = fields.One2many(
        comodel_name='setu.advance.budget.forecasted.position', inverse_name='setu_advance_budget_forecasted_id',
        string='', required=False)

    @api.depends('setu_advance_budget_forecasted_sheet_ids')
    def _get_total_count_forecasted_sheet(self):
        for budget_id in self:
            budget_id.total_forecasted_sheet = len(budget_id.setu_advance_budget_forecasted_sheet_ids)

    @api.depends('previous_budget_forecasted_ids')
    def _get_no_reaction_budget(self):
        for budget_id in self:
            budget_id.number_of_reaction_budget = len(budget_id.previous_budget_forecasted_ids)

    @api.depends('setu_advance_budget_forecasted_sheet_line_ids')
    def _get_total_count_forecasted_line(self):
        for budget_id in self:
            budget_id.total_forecasted_sheet_line = len(budget_id.setu_advance_budget_forecasted_sheet_line_ids)

    @api.depends('setu_advance_budget_forecasted_position_ids')
    def _get_total_count_forecasted_position(self):
        for budget_id in self:
            budget_id.total_forecasted_position = len(budget_id.setu_advance_budget_forecasted_position_ids)

    def action_budget_confirm(self):
        if not self.setu_advance_budget_forecasted_periods_ids:
            raise ValidationError(_('Please Calculate Forecasted Periods First'))

        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})

    def action_budget_create_periods(self, interval=1):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: create monthly perios according to select year in budget record
                     (button - create period)
        """
        setu_advance_budget_forecasted_periods_obj = self.env['setu.advance.budget.forecasted.periods']
        end_date = self.date_to.month
        if end_date != int(self.company_id.fiscalyear_last_month):
            raise ValidationError(_('Budget year should be according to the fiscal month of company.'))

        if self.setu_advance_budget_forecasted_periods_ids:
            self.setu_advance_budget_forecasted_periods_ids.unlink()
        ds = datetime.strptime(self.date_from.strftime('%Y-%m-%d'), '%Y-%m-%d')

        while ds.date() < self.date_to:
            de = ds + relativedelta(months=interval, days=-1)
            if de.date() > self.date_to:
                de = datetime.strptime(str(self.date_to), '%Y-%m-%d')

            setu_advance_budget_forecasted_periods_obj.create(
                {'forecasted_type': "planned", 'start_date': ds.strftime('%Y-%m-%d'),
                 'end_date': de.strftime('%Y-%m-%d'), 'setu_advance_budget_forecasted_id': self.id})
            ds = ds + relativedelta(months=interval)
        return True

    def action_view_forecasted_sheet(self):
        advance_budget_forecasted_sheet_ids = self.mapped('setu_advance_budget_forecasted_sheet_ids')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_advance_budget_management.setu_advance_budget_forecasted_sheet_action_open")
        action['context'] = {'default_setu_advance_budget_forecasted_id': self.id}
        action['domain'] = [('id', 'in', advance_budget_forecasted_sheet_ids.ids)]
        return action

    def action_view_forecasted_sheet_line(self):
        advance_budget_forecasted_sheet_line_ids = self.mapped('setu_advance_budget_forecasted_sheet_line_ids')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_advance_budget_management.setu_advance_budget_forecasted_sheet_line_action_open")
        action['context'] = {'default_setu_advance_budget_forecasted_id': self.id}
        action['domain'] = [('id', 'in', advance_budget_forecasted_sheet_line_ids.ids)]
        return action

    def action_view_forecasted_position(self):
        advance_budget_forecasted_position_ids = self.mapped('setu_advance_budget_forecasted_position_ids')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_advance_budget_management.setu_advance_budget_forecasted_position_action_open")
        action['context'] = {'default_setu_advance_budget_forecasted_id': self.id}
        action['domain'] = [('id', 'in', advance_budget_forecasted_position_ids.ids)]
        return action


    def action_show_forecasted_position_details(self):
        forecasted_positions = self.setu_advance_budget_forecasted_position_ids
        tree_view = self.env.ref('setu_advance_budget_management.setu_advance_budget_forecasted_position_tree_view')
        return {
            'name': _('Standard Reporting %s') % (self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'setu.advance.budget.forecasted.position',
            'views': [(tree_view.id, 'list')],
            'target': 'current',
            'domain': [('id', 'in', forecasted_positions.ids)]}

    def active_open_reaction_budget(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: To open new record of budget from budget record
        """
        pervious_budget_forecasted_ids = self.previous_budget_forecasted_ids
        tree_view = self.env.ref('setu_advance_budget_management.setu_advance_budget_forecasted_tree_view')
        return {
            'name': _('Budget %s') % (self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'setu.advance.budget.forecasted',
            'views': [(tree_view.id, 'list')],
            'target': 'current',
            'domain': [('id', 'in', pervious_budget_forecasted_ids.ids)]}

    def action_pre_filled_plan(self):
        """
            Author: udit@setuconsulting
            Date: 14/03/23
            Task: Agrobolder migration
            Purpose: set account and analytic accounts in sheet line as per configuration in setting
        """
        for rec in self:
            account_ids = self.env["ir.default"].sudo().get('res.config.settings', 'account_ids',
                                    company_id=self.env.company.id)
            acoount_ids_list = account_ids
            analytic_account_ids = self.env["ir.default"].sudo().get('res.config.settings', 'analytic_account_ids',
                                            company_id=self.env.company.id)
            analytic_account_ids_list = analytic_account_ids

            if not acoount_ids_list:
                raise ValidationError(_('Please select accounts in configuration to made sheets.'))

            for ana_acc in analytic_account_ids_list:
                analytic_account_id = self.env['account.analytic.account'].browse(ana_acc)
                for  acc in acoount_ids_list:
                    account_id = self.env['account.account'].browse(acc)
                    sheets = self.env['setu.advance.budget.forecasted.sheet'].search(
                        [('setu_advance_budget_forecasted_id', '=', rec.id), (
                            'analytic_account_id', '=', analytic_account_id.id)])

                    if sheets:
                        lines = sheets.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                            lambda line: line.analytic_account_id.id == analytic_account_id.id and line.account_id.id == account_id.id)
                        if not lines:
                            sheet_lines = self.env['setu.advance.budget.forecasted.sheet.line'].with_context(default_setu_advance_budget_forecasted_id=rec.id).create({
                                'setu_advance_budget_forecasted_sheet_id': sheets.id,
                                'analytic_account_id': analytic_account_id.id,
                                'account_id': account_id.id,
                            })

                    else:
                        new_sheet = self.env['setu.advance.budget.forecasted.sheet'].with_context(default_setu_advance_budget_forecasted_id=rec.id).create(
                            {'analytic_account_id': analytic_account_id.id,
                             'setu_advance_budget_forecasted_id': rec.id,
                             'planned_amount': 0.0})
                        vals = {'analytic_account_id': analytic_account_id.id, 'account_id': account_id.id,
                                'planned_amount': 0.0,'setu_advance_budget_forecasted_sheet_id': new_sheet.id}
                        sheet_lines = self.env['setu.advance.budget.forecasted.sheet.line'].with_context(
                            default_setu_advance_budget_forecasted_id=rec.id).create(vals)
            null_analytic_account_sheet = self.env['setu.advance.budget.forecasted.sheet'].search(
                [('setu_advance_budget_forecasted_id', '=', rec.id), (
                    'analytic_account_id', '=', False)])
            if not null_analytic_account_sheet:
                for acc in acoount_ids_list:
                    account_id = self.env['account.account'].browse(acc)
                    null_analytic_account_sheet = self.env['setu.advance.budget.forecasted.sheet'].search(
                        [('setu_advance_budget_forecasted_id', '=', rec.id), (
                            'analytic_account_id', '=', False)])
                    if null_analytic_account_sheet:
                        lines = null_analytic_account_sheet.setu_advance_budget_forecasted_sheet_line_ids.filtered(
                            lambda
                                line: line.analytic_account_id == False and line.account_id.id == account_id.id)
                        if not lines:
                            sheet_lines = self.env['setu.advance.budget.forecasted.sheet.line'].with_context(
                                default_setu_advance_budget_forecasted_id=rec.id).create({
                                'setu_advance_budget_forecasted_sheet_id': null_analytic_account_sheet.id,
                                'analytic_account_id': False,
                                'account_id': account_id.id,
                            })
                    else:
                        new_null_analytic_account_sheet = self.env['setu.advance.budget.forecasted.sheet'].with_context(
                            default_setu_advance_budget_forecasted_id=rec.id).create(
                            {'analytic_account_id': False,
                             'setu_advance_budget_forecasted_id': rec.id,
                             'planned_amount': 0.0})
                        vals = {'analytic_account_id': False, 'account_id': account_id.id,
                                'planned_amount': 0.0, 'setu_advance_budget_forecasted_sheet_id': new_null_analytic_account_sheet.id}
                        sheet_lines = self.env['setu.advance.budget.forecasted.sheet.line'].with_context(
                            default_setu_advance_budget_forecasted_id=rec.id).create(vals)

        return True

    def update_actual_data(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: update actual data of accounts selected in budget and according period of postions
        """
        for rec in self:
            for period in rec.setu_advance_budget_forecasted_position_ids:
                if period.analytic_account_id.id:
                    analytic_line_obj = self.env['account.analytic.line']
                    domain = [('account_id', '=', period.analytic_account_id.id),
                              ('date', '>=', period.start_date),
                              ('date', '<=',period.end_date),('general_account_id', '=', period.account_id.id)
                              ]
                    where_query = analytic_line_obj._where_calc(domain)
                    analytic_line_obj._apply_ir_rules(where_query, 'read')
                    from_clause, where_clause, where_clause_params = where_query.get_sql()
                    select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause
                else:
                    aml_obj = self.env['account.move.line']
                    domain = [('account_id', '=',
                               period.account_id.id),
                              ('date', '>=', period.start_date),
                              ('date', '<=', period.end_date),
                              ('parent_state', '=', 'posted')
                              ]
                    where_query = aml_obj._where_calc(domain)
                    aml_obj._apply_ir_rules(where_query, 'read')
                    from_clause, where_clause, where_clause_params = where_query.get_sql()
                    if period.account_id.account_type not in ('income', 'other_income'):
                        select = "SELECT sum(debit)-sum(credit) from " + from_clause + " where " + where_clause
                    else:
                        select = "SELECT sum(credit)-sum(debit) from " + from_clause + " where " + where_clause
                self.env.cr.execute(select, where_clause_params)
                period.amount_in_journal_items = self.env.cr.fetchone()[0] or 0.0


        return True