from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'


    def reverse_moves(self, is_modify=False):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/02/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86duhapac)
            Purpose: to set the fields as per the documentation.
        """
        active_id = self.env.context.get('active_id')
        account_id = self.env['account.move'].browse(active_id)

        res = super(AccountMoveReversal, self).reverse_moves(is_modify)
        if account_id.move_type == 'out_invoice':
            account_move_line_obj = self.env['account.move.line']
            account_tax_obj = self.env['account.tax']
            credit_note_id = self.env['account.move'].browse(res.get('res_id'))

            ir_config_parameter_obj = self.env['ir.config_parameter'].sudo()
            product_iva_16_percentage_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.product_id_for_iva_16_percentage')
            product_iva_0_percentage_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.product_id_for_iva_0_percentage')
            vat_configuration = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.vat_configuration')
            cancel_reason_conf_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.cancel_reason_conf_id')
            country_conf_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.country_conf_id')
            l10n_mx_edi_payment_method_conf_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.l10n_mx_edi_payment_method_conf_id')
            iva_sixteen_percentage_tax_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.iva_sixteen_percentage_tax_id')
            iva_zero_percentage_tax_id = ir_config_parameter_obj.get_param(
                'setu_accounts_report_extended.iva_zero_percentage_tax_id')
            if not (
                    product_iva_16_percentage_id and product_iva_0_percentage_id and vat_configuration and cancel_reason_conf_id and country_conf_id and l10n_mx_edi_payment_method_conf_id and iva_sixteen_percentage_tax_id and iva_zero_percentage_tax_id):
                raise ValidationError(_("Please Select The values of configuration first then apply this."))

            if credit_note_id and self.reason_id.id == int(cancel_reason_conf_id):
                if credit_note_id.partner_id.vat == vat_configuration or credit_note_id.partner_id.country_id.id != int(country_conf_id):
                    credit_note_id.l10n_mx_edi_usage = 'S01'
                elif credit_note_id.partner_id.vat != vat_configuration and credit_note_id.partner_id.country_id.id == int(country_conf_id):
                    credit_note_id.l10n_mx_edi_usage = 'G02'
                credit_note_id.write({'l10n_mx_edi_payment_method_id':int(l10n_mx_edi_payment_method_conf_id)})

                iva_sixteen_percentage_tax = account_tax_obj.browse(int(iva_sixteen_percentage_tax_id))
                iva_zero_percentage_tax = account_tax_obj.browse(int(iva_zero_percentage_tax_id))

                line_vals = {'move_id': credit_note_id.id}
                sixteen_ventas_tax_line_ids = credit_note_id.invoice_line_ids.filtered(lambda sixteen:sixteen.tax_ids == iva_sixteen_percentage_tax)
                zero_ventas_tax_line_ids = credit_note_id.invoice_line_ids.filtered(lambda zero: zero.tax_ids == iva_zero_percentage_tax)
                if sixteen_ventas_tax_line_ids:
                    sixteen_ventas_tax_line_ids.unlink()
                    line_vals.update({
                        'product_id': int(
                            product_iva_16_percentage_id),
                    })
                    account_move_line_obj.create(line_vals)

                if zero_ventas_tax_line_ids:
                    zero_ventas_tax_line_ids.unlink()
                    line_vals.update({
                        'product_id': int(
                            product_iva_0_percentage_id),
                    })
                    account_move_line_obj.create(line_vals)
                account_id.write({'is_bonificacion': True})
        return res