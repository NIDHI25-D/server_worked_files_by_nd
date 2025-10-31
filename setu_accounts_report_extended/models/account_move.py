from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import format_date
from odoo.exceptions import UserError
import pytz
import logging

_logger = logging.getLogger('vendor_bills')


class AccountMove(models.Model):
    _inherit = 'account.move'

    related_po = fields.Many2one('purchase.order', string='Related PO',
                                 domain="[('state', 'in', ('purchase', 'done'))]")
    payment_date = fields.Date(compute='_compute_payment_date', store=True)
    schedule_date = fields.Date(string="Schedule date", help='Enter schedule date to confirm bill', copy=False)
    related_so_id = fields.Many2one('sale.order', string="Related SO", domain="[('state', 'in', ('sale','done'))]")
    is_bonificacion = fields.Boolean(string="Is Bonificacion?")
    l10n_mx_currency_rate = fields.Float(copy=False, digits=(16, 2),
                                         store=True, compute='_set_mx_currency_rate',
                                         string="Currency Rate MX")

    def _l10n_mx_edi_get_tax_objected(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 03/03/25
            Task: Migration from V16 to V18
            Purpose: returning the usage.
            Used to determine the IEPS tax breakdown in CFDI
             01 - Used by foreign partners not subject to tax
             02 - Default for MX partners. Splits IEPS taxes
             03 - Special override when IEPS split / Taxes are not required
        """
        self.ensure_one()
        customer = self.partner_id if self.partner_id.type == 'invoice' else self.partner_id.commercial_partner_id
        if customer.l10n_mx_edi_no_tax_breakdown:
            return '03'
        elif (self.move_type in self.get_invoice_types() and not self.invoice_line_ids.tax_ids) or \
             (self.move_type == 'entry' and not self._get_reconciled_invoices().invoice_line_ids.tax_ids):
            # the invoice has no taxes OR for payments and bank statement lines, the reconciled invoices have no taxes
            return '01'
        else:
            return '02'

    @api.depends('currency_id')
    def _set_mx_currency_rate(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 12/02/25
            Task: Migration from V16 to V18
            Purpose: We set the l10n_mx_currency_rate value with the accounting date.
            This should be done after invoice has been posted
            to have the proper accounting date.
        """
        for rec in self:
            if rec.company_id.currency_id == rec.currency_id:
                rec.l10n_mx_currency_rate = 1.0
            else:
                rec.l10n_mx_currency_rate = rec.currency_id._convert(
                    1.0, rec.company_id.currency_id,
                    rec.company_id, rec.date, round=False)

    @api.onchange('date')
    def _onchange_date(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 12/02/25
            Task: Migration from V16 to V18
            Purpose: Not to post invoices if date is lower or equal than lock date.
        """
        for move in self:
            journal = move.journal_id or self.env['account.journal'].search([],limit=1)
            lock_date = move.company_id._get_user_fiscal_lock_date(journal)
            if move.date <= lock_date:
                if self.env.user.has_group('account.group_account_manager'):
                    message = _("You cannot add/modify entries prior "
                                "to and inclusive of the lock date %s.",
                                format_date(self.env, lock_date))
                else:
                    message = _(
                        "You cannot add/modify entries prior to and inclusive"
                        " of the lock date %s. Check the company settings or "
                        "ask someone with the 'Adviser' role",
                        format_date(self.env, lock_date))
                raise UserError(message)

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payment_date(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/02/25
              Task: Migration from V16 to V18
              Purpose: To set payment date which invoice are paid.
        """
        for inv in self:
            dates = []
            if inv.invoice_payments_widget and inv.move_type == 'out_invoice':
                for content in inv.invoice_payments_widget.get('content'):
                    dates.append(content.get('date'))
                inv.payment_date = list(sorted(dates))[-1]
            else:
                inv.payment_date = False

    def confirm_bill_on_schedule_date(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/02/25
              Task: Migration from V16 to V18
              Purpose: posting the bills through the schedule action.
        """
        bill_ids = self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'draft'), (
            'schedule_date', '=', datetime.now().astimezone(pytz.timezone('America/Mexico_City')).date())])
        _logger.info(f"{bill_ids}")

        for bill in bill_ids:
            bill.invoice_date = datetime.now().astimezone(pytz.timezone('America/Mexico_City')).date()
            bill._get_accounting_date(bill.invoice_date, bill._affect_tax_report())
            for line in bill.line_ids:
                balance = line.company_id.currency_id.round(line.amount_currency / line.currency_rate)
                line.balance = balance
            bill.action_post()
        return True
