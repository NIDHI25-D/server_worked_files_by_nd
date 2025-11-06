from odoo import fields, models


class NetworkCardType(models.Model):
    _name = 'network.card.type'
    _description = 'Network Card Type'

    name = fields.Char()
    asset_id = fields.Many2one('account.asset')
    network_card_mac_address_ids = fields.Many2many('network.card.mac.address')
