# coding: utf-8
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_mx_edi_cfdi_to_public = fields.Boolean(
        string="CFDI to public",
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Override."""
        params = super()._load_pos_data_fields(config_id)
        params += ["l10n_mx_edi_cfdi_to_public"]
        return params