# See LICENSE file for full copyright and licensing details.


from odoo import api, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self):
        """
            Author: jay.garach@setuconsulting.com
            Date:  20/12/24
            Task: Migration from V16 to V18
            Purpose: (1) raise error if customer have not over credit limit option
                     debit amount - which customer have to pay to the company
                     credit amount - which company have to pay to the customer
                     if debit amount + (confirmed order amount which have not invoiced) - credit amount
                     is greater than partner credit limit
        """
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if (user_id and not user_id.has_group('base.group_portal')) or not user_id:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id), ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                 ('parent_state', '=', 'posted'), ('reconciled', '!=', True)]
            )
            confirm_sale_order = self.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'sale'),
                 ('invoice_status', '!=', 'invoiced')])
            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                credit += line.credit
                debit += line.debit

            partner_credit_limit = (debit + amount_total) - credit
            available_credit_limit = round(partner.credit_limit - partner_credit_limit, 2)
            if partner_credit_limit > partner.credit_limit > 0.0:
                if not partner.over_credit:
                    if self._context.get('from_monthly_cron') and (self.is_monthly_proposal or self.is_monthly_interval_proposal):
                        self.with_context(bypass_from_check_limit=True)
                        return  False
                    msg = 'Your available credit limit Amount = %s \nCheck "%s" Accounts or Credit ' \
                          'Limits.' % (available_credit_limit, self.partner_id.name)
                    raise UserError(_('You can not confirm Sale Order. \n' + msg))
            return True

    def action_confirm(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: check credit limit of non-website order.
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.website_id:
                order.check_limit()
        return res

    @api.constrains('amount_total', 'partner_id')
    def check_amount(self):
        for order in self:
            if not order.is_monthly_proposal:
                order.check_limit()

