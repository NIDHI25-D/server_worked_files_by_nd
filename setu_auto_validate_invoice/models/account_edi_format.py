from odoo import models


class AccountEdiFormat(models.Model):
    _inherit = 'l10n_mx_edi.document'

    # def _l10n_mx_edi_get_invoice_cfdi_values(self, invoice):
    #     # OVERRIDE
    #     """
    #         Author: udit@setuconsulting
    #         Date: 09/05/23
    #         Task: mvsa migration
    #         Purpose: override currency conversion rate as per calculated l10n_mx_currency_rate
    #     """
    #     vals = super()._l10n_mx_edi_get_invoice_cfdi_values(invoice)
    #     if invoice.currency_id.name != 'MXN':
    #         vals['currency_conversion_rate'] = invoice.l10n_mx_currency_rate
    #     return vals

