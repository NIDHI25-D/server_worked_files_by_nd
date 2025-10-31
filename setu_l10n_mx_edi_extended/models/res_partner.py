from odoo import fields, models, api


class ResPartnerExt(models.Model):
    _inherit = "res.partner"

    # disable_inv_automatic_sign = fields.Boolean(
    #     string='Disable Invoice Automatically signed',
    #     help="Check this to disable automatically sign invoice for this customer")--> as taken at auto validate invoice
    l10n_mx_edi_fiscal_regime = fields.Selection(selection_add=[
        ('foreign_customer', 'No Fiscal Obligations'),
    ])

    @api.onchange('fiscal_position_id', 'property_account_position_id')
    def _onchange_fiscal_position_id_or_property_account_position_id(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 21/02/25
            Task: Migration to v18 from v16
            Purpose: Automation of the fiscal position within the contacts.
        """
        self._origin.fiscal_position_id = self.property_account_position_id
        if self.fiscal_position_id.id and self.property_account_position_id.id:
            self._origin.l10n_mx_edi_fiscal_regime = False
            try:
                code = int(self._origin.fiscal_position_id.name.split(' ')[0])
                self._origin.l10n_mx_edi_fiscal_regime = str(code)
            except:
                self._origin.l10n_mx_edi_fiscal_regime = '601'

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 21/02/25
            Task: Migration to v18 from v16
            Purpose: Automation of the fiscal position within the contacts when partner are creates.
        """
        res = super(ResPartnerExt, self).create(vals_list)
        for res_id in res:
            if res_id.property_account_position_id:
                res_id._onchange_fiscal_position_id_or_property_account_position_id()
        return res