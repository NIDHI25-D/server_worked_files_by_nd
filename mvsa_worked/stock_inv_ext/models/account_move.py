from odoo import api, fields, models, tools


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _calculate_custom_number(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: set custom number of the landed cost record in invoice line
        """
        date_custom_number = ""
        landed_obj = self.env['stock.landed.cost']

        for line in self.mapped('invoice_line_ids').filtered('sale_line_ids'):
            date_custom_number = ""
            moves = line.mapped('sale_line_ids.move_ids').filtered(
                lambda r: r.state == 'done' and not r.scrapped)
            landed = landed_obj.search(
                [('picking_ids', 'in',
                  moves.mapped('move_orig_fifo_ids.picking_id').ids), ('l10n_mx_edi_customs_number', '!=', False)])
            if not moves or not landed:
                continue

            line.l10n_mx_edi_customs_number = ','.join(list(set(landed.mapped('l10n_mx_edi_customs_number'))))

            for i in list(set(landed.mapped('date_custom_numbers'))):
                if i:
                    date_custom_number = date_custom_number + ", Fecha Pedimento: " + i
            line.name += date_custom_number
        return True

    def _post(self, soft=True):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: set custom number of the landed cost during validate.
        """
        self._calculate_custom_number()
        res = super(AccountInvoice, self)._post(soft=soft)
        for move in self:
            if move.is_invoice() and move.partner_id.property_account_position_id.name == 'Foreign Customer' and self.l10n_mx_edi_external_trade_type == '02':
                for line in move.line_ids:
                    line.l10n_mx_edi_customs_number = ''
        return res


    def _get_accounting_date(self, invoice_date, has_tax, lock_dates=None):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: Used for set the date same as invoice date.
        """
        res = super(AccountInvoice, self)._get_accounting_date(invoice_date, has_tax, lock_dates)
        res = self.invoice_date if self.invoice_date else res
        return res