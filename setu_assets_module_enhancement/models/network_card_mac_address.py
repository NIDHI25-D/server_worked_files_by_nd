from odoo import fields, models


class NetworkCardMacAddress(models.Model):
    _name = 'network.card.mac.address'
    _description = 'Network Card Mac Address'

    name = fields.Char()
    asset_id = fields.Many2one('account.asset')
