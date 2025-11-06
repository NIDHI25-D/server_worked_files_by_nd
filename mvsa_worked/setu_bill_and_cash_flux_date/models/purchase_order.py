from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_importation_tax = fields.Float(compute='_calculate_total_taxes', string='Total importation taxes', store=True)

    @api.depends('total_iva', 'cc_procedure_dta', 'total_igi')
    def _calculate_total_taxes(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 04/02/25
            Task: Migration from V16 to V18
            Purpose: Setting The Total Of importation taxes.
        """
        for po in self:
            po.total_importation_tax = sum([po.total_iva, po.cc_procedure_dta, po.total_igi])
        return True

    def button_confirm(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 04/02/25
            Task: Migration from V16 to V18
            Purpose: Creating the vendor bill upon purchase payments of payment term
            Upon the partner tags if the Enable for create bill is true then only it will create Bills.
        """
        res = super().button_confirm()
        for order in self:
            enable_for_create_bill = order.partner_id.category_id.filtered(lambda x: x.is_enable_for_create_bill)
            bill_type_ids = order.payment_term_id.purchase_payment_ids
            if enable_for_create_bill and bill_type_ids:
                self.create_vendor_bill(bill_type_ids)
        return res

    def create_vendor_bill(self, bill_type_ids):
        """
            Author: jay.garach@setuconsulting.com
            Date: 04/02/25
            Task: Migration from V16 to V18
            Purpose: filtering the bill typs that are going to create the vendor bills.
            creating the vendor bill for whose currency is same and create bill draft is set to true.
            after that vendor tax bill for whose tax type is set to true.
            it only creates a vendor tax bill if not created with the same bill type.
        """
        move_type = self._context.get('default_move_type', 'in_invoice')
        enable_bill_draft_ids = bill_type_ids.filtered(
            lambda x: x.is_create_bill_draft and x.bill_id.currency_id == self.currency_id)
        enable_tax_draft_bill_ids = bill_type_ids.filtered(lambda x: x.bill_id.is_it_tax_type)
        created_invoices = []
        for enable_bill_draft_id in enable_bill_draft_ids:
            date = self[enable_bill_draft_id.date_type]
            invoice = self.env['account.move'].browse(created_invoices)
            if created_invoices and enable_bill_draft_id.bill_id.id in invoice.mapped('bill_id.id'):
                continue
            if not date:
                data_type = dict(enable_bill_draft_id._fields['date_type'].selection).get(
                    enable_bill_draft_id.date_type)
                raise UserError(_(f"{data_type} is not set in purchase order."))
            bill_vals = self.prepare_bill_value(enable_bill_draft_id, move_type, date)
            invoice_id = self.env['account.move'].create([bill_vals])
            created_invoices.append(invoice_id.id)
        if created_invoices and enable_tax_draft_bill_ids:
            for enable_bill_tax_id in enable_tax_draft_bill_ids:
                move_id = self.env['account.move'].search([('bill_id', '=', enable_bill_tax_id.bill_id.id), ('id', 'in', created_invoices)])
                if move_id:
                    continue
                else:
                    date = self[enable_bill_tax_id.date_type]
                    if not date:
                        data_type = dict(enable_bill_tax_id._fields['date_type'].selection).get(
                            enable_bill_tax_id.date_type)
                        raise UserError(_(f"{data_type} is not set in purchase order."))
                    bill_vals = self.prepare_bill_value(enable_bill_tax_id, move_type, date)
                    invoice_id = self.env['account.move'].create([bill_vals])
                    created_invoices.append(invoice_id.id)
        return True

    def prepare_bill_value(self, bill_draft_id, move_type, date):
        """
            Author: jay.garach@setuconsulting.com
            Date: 04/02/25
            Task: Migration from V16 to V18
            Purpose: Creating the Vals For Vendor Bill and Vendor Bill lines.
        """
        partner_invoice = self.env['res.partner'].browse(self.partner_id.address_get(['invoice'])['invoice'])
        partner_bank_id = self.partner_id.commercial_partner_id.bank_ids.filtered_domain(
            ['|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)])[:1]
        final_date = date + timedelta(days=bill_draft_id.days_quantity) if bill_draft_id.operation_type == 'add'\
            else date - timedelta(days=bill_draft_id.days_quantity)
        invoice_line_vals = {
            'name': '%s' % self.name,
            'product_id': bill_draft_id.bill_id.product_id.id,
            'account_id': bill_draft_id.bill_id.account_id.id,
            'analytic_distribution': {str(bill_draft_id.bill_id.analytic_id.id): 100.0}
        }
        invoice_vals = {
            'ref': bill_draft_id.bill_reference,
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': bill_draft_id.bill_id.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id or self.env.user.id,
            'partner_id': partner_invoice.id if bill_draft_id.is_vendor else False,
            'fiscal_position_id': (
                    self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(partner_invoice)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': partner_bank_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, invoice_line_vals)],
            'journal_id': bill_draft_id.bill_id.journal_id.id,
            'company_id': self.company_id.id,
            'related_po': self.id,
            'bill_id': bill_draft_id.bill_id.id,
            'invoice_date_due': final_date,
            'invoice_payment_term_id': False
        }
        return invoice_vals

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 04/02/25
            Task: Migration from V16 to V18
            Purpose: Updating the Invoice Due Date Upon some Conditions.
            Conditions Have to match as follows.
            If the date updated in PO is mentioned in the payment term, and also a bill type is the same,
            and its invoice is in draft state.
        """
        dates = [(key, vals.get(key)) for key in ['date_approve', 'delivery_date', 'vendor_bill_date', 'bl_date', 'bl_date_at_sight', 'date_planned'] if key in vals]
        res = super().write(vals)
        if dates and self.state in ('purchase', 'done') and self.account_move_ids:
            payment_terms = self.payment_term_id.purchase_payment_ids.filtered(
                lambda x: x.bill_id in self.account_move_ids.bill_id and not x.is_create_bill_draft)
            for date in dates:
                try:
                    final_date = datetime.strptime(date[1], '%Y-%m-%d %H:%M:%S')
                    final_date = final_date.date()
                except:
                    final_date = datetime.strptime(date[1], '%Y-%m-%d') if not isinstance(date[1], datetime) else \
                        date[1].date()
                for payment in payment_terms:
                    invoice_ids = self.account_move_ids.filtered(lambda x: x.bill_id == payment.bill_id and payment.date_type == date[0] and x.state == 'draft')
                    for invoice in invoice_ids:
                        invoice.write({
                            'invoice_date_due': final_date + timedelta(
                                days=payment.days_quantity-1) if payment.operation_type == 'add' else final_date - timedelta(
                                days=payment.days_quantity+1)
                        })
        return res
