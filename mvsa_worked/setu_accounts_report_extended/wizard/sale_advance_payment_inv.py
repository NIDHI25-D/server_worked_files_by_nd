# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import ValidationError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'


    def _create_invoices(self, sale_orders):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/02/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86dum7nc0)
            Purpose: to set the fields as per the documentation and separate credit note as per the taxes.
        """
        invoices = super()._create_invoices(sale_orders)

        ir_config_parameter_obj = self.env['ir.config_parameter'].sudo()
        vat_configuration = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.vat_configuration')
        country_conf_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.country_conf_id')
        l10n_mx_edi_payment_method_conf_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.l10n_mx_edi_payment_method_conf_id')
        iva_sixteen_percentage_tax_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.iva_sixteen_percentage_tax_id')
        iva_zero_percentage_tax_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.iva_zero_percentage_tax_id')
        journal_id_for_16_percent_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.journal_id_for_16_percent_id')
        journal_id_for_0_percent_id = ir_config_parameter_obj.get_param(
            'setu_accounts_report_extended.journal_id_for_0_percent_id')

        for invoice in invoices:
            if invoice and invoice.move_type == 'out_refund':
                if not (vat_configuration and country_conf_id and l10n_mx_edi_payment_method_conf_id and iva_sixteen_percentage_tax_id and iva_zero_percentage_tax_id and journal_id_for_16_percent_id and journal_id_for_0_percent_id):
                    raise ValidationError(
                        _("Please Select The values of configuration first then apply this for credit notes."))
                products_without_journal = invoice.invoice_line_ids.filtered(lambda line: line.product_id.type == 'consu' and not line.product_id.journal_id)
                if products_without_journal:
                    raise ValidationError(
                        _("Please set The values of journal in products in invoice lines first then apply this for credit notes."))
                all_taxes_of_lines = invoice.line_ids.tax_ids.mapped('id')
                zero_tax_ids = invoice.line_ids.filtered(lambda zero: int(iva_zero_percentage_tax_id) in zero.tax_ids.ids)
                if len(all_taxes_of_lines) > 1:
                    dup_invoice = invoice.copy()
                    sixteen_percent_tax_lines = dup_invoice.line_ids.filtered(
                        lambda sixteen: int(iva_sixteen_percentage_tax_id) in sixteen.tax_ids.ids)
                    if sixteen_percent_tax_lines:
                        sixteen_percent_tax_lines.unlink()
                    current_journal_of_dup_account = dup_invoice.journal_id.id
                    dup_invoice.write({
                        'journal_id': dup_invoice.invoice_line_ids[0].product_id.journal_id.id if
                        dup_invoice.invoice_line_ids[0].product_id and dup_invoice.invoice_line_ids[
                            0].product_id.journal_id else current_journal_of_dup_account,
                        'l10n_mx_edi_payment_method_id': int(l10n_mx_edi_payment_method_conf_id)
                    })
                    if (
                            dup_invoice.journal_id.id == int(journal_id_for_0_percent_id) and dup_invoice.partner_id.vat == vat_configuration) or dup_invoice.partner_id.country_id.id != int(country_conf_id):
                        dup_invoice.l10n_mx_edi_usage = 'S01'
                    elif dup_invoice.journal_id.id == int(journal_id_for_0_percent_id) and dup_invoice.partner_id.vat != vat_configuration and dup_invoice.partner_id.country_id.id == int(country_conf_id):
                        dup_invoice.l10n_mx_edi_usage = 'G02'
                    for idx, invoice_line in enumerate(invoice.invoice_line_ids.filtered(
                            lambda zero: int(iva_zero_percentage_tax_id) in zero.tax_ids.ids), start=0):
                        current_account_of_dup_account_line = dup_invoice.invoice_line_ids[idx].account_id.id
                        dup_invoice.invoice_line_ids[idx].write(
                            {'sale_line_ids': [(6, 0, invoice_line.sale_line_ids.ids)],
                             'account_id': dup_invoice.invoice_line_ids[
                                 idx].product_id.journal_id.default_account_id.id if dup_invoice.invoice_line_ids[
                                                                                         idx].product_id and
                                                                                     dup_invoice.invoice_line_ids[
                                                                                         idx].product_id.journal_id and
                                                                                     dup_invoice.invoice_line_ids[
                                                                                         idx].product_id.journal_id.default_account_id else current_account_of_dup_account_line})

                    if zero_tax_ids:
                        zero_tax_ids.unlink()
                current_journal_of_account = invoice.journal_id.id
                product_tax_id = invoice.invoice_line_ids.filtered(
                    lambda line: line.product_id.type == 'consu' and line.product_id.journal_id).tax_ids
                invoice.write({
                    'journal_id': invoice.invoice_line_ids[0].product_id.journal_id.id if invoice.invoice_line_ids[0].product_id and invoice.invoice_line_ids[0].product_id.journal_id else current_journal_of_account,
                    'l10n_mx_edi_payment_method_id': int(l10n_mx_edi_payment_method_conf_id)
                })
                if product_tax_id.id == int(iva_sixteen_percentage_tax_id):
                    if (
                            invoice.journal_id.id == int(journal_id_for_16_percent_id) and invoice.partner_id.vat == vat_configuration) or invoice.partner_id.country_id.id != int(country_conf_id):
                        invoice.l10n_mx_edi_usage = 'S01'
                    elif invoice.journal_id.id == int(journal_id_for_16_percent_id) and invoice.partner_id.vat != vat_configuration and invoice.partner_id.country_id.id == int(country_conf_id):
                        invoice.l10n_mx_edi_usage = 'G02'
                elif product_tax_id.id == int(iva_zero_percentage_tax_id):
                    if (
                            invoice.journal_id.id == int(journal_id_for_0_percent_id) and invoice.partner_id.vat == vat_configuration) or invoice.partner_id.country_id.id != int(country_conf_id):
                        invoice.l10n_mx_edi_usage = 'S01'
                    elif invoice.journal_id.id == int(journal_id_for_0_percent_id) and invoice.partner_id.vat != vat_configuration and invoice.partner_id.country_id.id == int(country_conf_id):
                        invoice.l10n_mx_edi_usage = 'G02'
                for line in invoice.invoice_line_ids:
                    current_account_of_account_line = line.account_id.id
                    line.write({
                        'account_id': line.product_id.journal_id.default_account_id.id if line.product_id and line.product_id.journal_id and line.product_id.journal_id.default_account_id else current_account_of_account_line
                    })
        return invoices
