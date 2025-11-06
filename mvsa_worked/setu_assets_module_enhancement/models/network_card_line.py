from odoo import fields, models, api

class NetworkCardLine(models.Model):
    _name = 'network.card.line'
    _description = 'Network Card Line'

    asset_id = fields.Many2one('account.asset')
    network_card_type_id = fields.Many2one('network.card.type')
    network_card_mac_address_ids = fields.Many2many('network.card.mac.address', 'network_card_mac_address_relation')
