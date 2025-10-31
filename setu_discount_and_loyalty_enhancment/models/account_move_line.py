from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_reward_line = fields.Boolean('Is a program reward line')
    reward_id = fields.Many2one('loyalty.reward', ondelete='restrict', readonly=True)

    def _compute_account_id(self):
        """
        Author: Biren V Chauhan | Date: 15/08/23 | Task: https://app.clickup.com/t/86duc3hy0?comment=90170071813920
        Purpose: to set the invoiced E-wallet line account as per set in taxes for E-wallet.
        """
        super(AccountMoveLine, self)._compute_account_id()
        having_ewallet_lines = self.filtered(
            lambda x: x.is_reward_line and x.reward_id.program_id.program_type == 'ewallet')
        if having_ewallet_lines:
            for line in having_ewallet_lines:
                if line.tax_ids.ewallet_invoice_account_id:
                    line.account_id = line.tax_ids.ewallet_invoice_account_id.id
