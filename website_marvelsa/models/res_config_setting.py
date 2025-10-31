from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    abondend_cart_deleting_days = fields.Integer(string="Days Configure for Abondends carts deleting cron",
                                                 config_parameter='website_marvelsa.abondend_cart_deleting_days',
                                                 default=1)

