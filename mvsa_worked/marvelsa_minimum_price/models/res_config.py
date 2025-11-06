from odoo import fields, models


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_minimum_price = fields.Boolean("Enable Minimum Price", default=False, config_parameter="marvelsa_minimum_price.enable_minimum_price")
