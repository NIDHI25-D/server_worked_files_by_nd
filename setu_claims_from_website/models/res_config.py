from odoo import models, fields, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_claim = fields.Boolean("Enable Claims", config_parameter='setu_claims_from_website.enable_claim')
    # can't review the usage
    # days_to_calculate = fields.Integer(string="Day To Calculate",
    #                                    config_parameter='setu_claims_from_website.days_to_calculate')
    claim_report_address = fields.Char(string="Claim Report Address",
                                       config_parameter='setu_claims_from_website.claim_report_address')
