# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def get_sale_l10n_mx_edi_usage(self):
        """
        Author: kamlesh.singh@setuconsulting.com
        Date: 29-01-2024
        Task: CFDI and payment Way Migration v16 to v18
        Purpose : This method will used to get value of the field
        :return: fields value
        """
        return dict(self._fields['l10n_mx_edi_usage'].selection).get(self.l10n_mx_edi_usage)
