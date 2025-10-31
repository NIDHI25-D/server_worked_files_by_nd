from odoo import api, fields, models, _
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_ids = fields.Many2many("account.account",domain = [('account_type','in',('income','income_other','expense','expense_depreciation','expense_direct_cost'))], string="Accounts")
    analytic_account_ids = fields.Many2many("account.analytic.account",string = "Analytic Accounts")

    @api.model
    def get_values(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: get value of accounts and analytic accounts from setting
        """
        res = super(ResConfigSettings, self).get_values()

        IrDefault = self.env['ir.default'].sudo()
        account_ids = IrDefault.get('res.config.settings', 'account_ids',
                                    company_id=self.env.company.id)
        analytic_account_ids = IrDefault.get('res.config.settings', 'analytic_account_ids',
                                            company_id=self.env.company.id)
        res.update(account_ids=[(6, 0, account_ids or [])]
                   ,analytic_account_ids=[(6, 0, analytic_account_ids or [])])
        return res

    def set_values(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: set value of accounts and analytic accounts from setting
        """
        res = super(ResConfigSettings, self).set_values()

        IrDefault = self.env['ir.default'].sudo()

        IrDefault.set('res.config.settings', 'account_ids', self.account_ids.ids or [],
                      company_id=self.env.company.id)
        IrDefault.set('res.config.settings', 'analytic_account_ids',
                      self.analytic_account_ids.ids or [],
                      company_id=self.env.company.id)
        return res
