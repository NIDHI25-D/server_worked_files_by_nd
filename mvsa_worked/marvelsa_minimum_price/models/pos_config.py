from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_disable_minimum_price = fields.Boolean("Enable Minimum Price")
