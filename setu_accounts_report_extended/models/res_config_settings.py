from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_id_for_iva_16_percentage = fields.Many2one('product.product',
                                                       config_parameter='setu_accounts_report_extended.product_id_for_iva_16_percentage',
                                                       string="Product IVA 16%")
    product_id_for_iva_0_percentage = fields.Many2one('product.product',
                                                      config_parameter='setu_accounts_report_extended.product_id_for_iva_0_percentage',
                                                      string="Product IVA 0%")
    vat_configuration = fields.Char(string="Tax ID Configuration",
                                    config_parameter='setu_accounts_report_extended.vat_configuration')
    cancel_reason_conf_id = fields.Many2one('setu.invoice.cancel', config_parameter='setu_accounts_report_extended.cancel_reason_conf_id',
                                            string="Cancellation Reason Configuration")
    country_conf_id = fields.Many2one('res.country', config_parameter='setu_accounts_report_extended.country_conf_id',
                                      string='Country Configuration')
    l10n_mx_edi_payment_method_conf_id = fields.Many2one('l10n_mx_edi.payment.method', config_parameter='setu_accounts_report_extended.l10n_mx_edi_payment_method_conf_id',
                                                         string='Payment Way Configuration')
    iva_sixteen_percentage_tax_id = fields.Many2one('account.tax', config_parameter='setu_accounts_report_extended.iva_sixteen_percentage_tax_id',
                                                    string='IVA 16% VENTAS Configuration')
    iva_zero_percentage_tax_id = fields.Many2one('account.tax', config_parameter='setu_accounts_report_extended.iva_zero_percentage_tax_id',
                                                 string='IVA 0% VENTAS Configuration')
    journal_id_for_16_percent_id = fields.Many2one('account.journal',
                                                config_parameter='setu_accounts_report_extended.journal_id_for_16_percent_id',
                                                string="Journal for 16% Ventas")
    journal_id_for_0_percent_id = fields.Many2one('account.journal',
                                               config_parameter='setu_accounts_report_extended.journal_id_for_0_percent_id',
                                               string="Journal for 0% Ventas")
    selected_journal_ids = fields.Many2many('account.journal',string="Journals")



    @api.model
    def get_values(self):
        """
            Author: nidhi@setconsulting.com
            Date: 24/09/25
            Task: customer statement missing column {https://app.clickup.com/t/86dxby19n} comment==> {https://app.clickup.com/t/86dxby19n?comment=90170149395014}
            Purpose: get the value of selected_journal_ids in settings.
        """
        res = super(ResConfigSettings, self).get_values()
        selected_journal_ids = self.env['ir.config_parameter'].sudo().get_param('setu_accounts_report_extended.selected_journal_ids')
        if selected_journal_ids:
            res['selected_journal_ids'] = [(6, 0, eval(selected_journal_ids))]
        return res

    def set_values(self):
        """
            Author: nidhi@setconsulting.com
            Date: 24/09/25
            Task: customer statement missing column {https://app.clickup.com/t/86dxby19n} comment==> {https://app.clickup.com/t/86dxby19n?comment=90170149395014}
            Purpose: set the value of selected_journal_ids in settings to save the record of many2many field.
        """
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'setu_accounts_report_extended.selected_journal_ids',
            self.selected_journal_ids.ids)
        return res
