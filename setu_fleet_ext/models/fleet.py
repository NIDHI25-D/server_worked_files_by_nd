# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetExtended(models.Model):
    _inherit = 'fleet.vehicle'

    economic_number = fields.Char(string='Economic Number', required=False, index='trigram')
    last_location = fields.Text(string="Last Location", required=False)
    combustible_card_type_id = fields.Many2one('combustible.card.type', ondelete="restrict")
    combustible_card_number = fields.Char(string="Combustible Card Number", index='trigram')
    pase_tag_id = fields.Many2one('pase.tag', ondelete="restrict")
    pase_tag_number = fields.Char("Pase Tag Number", index='trigram')
    combustible_pin_type_id = fields.Many2one('combustible.pin.type', string="Combustible Pin Type",
                                              ondelete="restrict")
    combustible_pin_number = fields.Char(index='trigram')
    vehicle_type_id = fields.Many2one('fleet.vehicle.tag', string="Vehicle Type")
    vehicle_setup_id = fields.Many2one('l10n_mx_edi.vehicle', string="Vehicle Setup", ondelete="restrict")
    vehicle_config = fields.Selection(related="vehicle_setup_id.vehicle_config", string='Vehicle Configuration',
                                      help='The type of vehicle used')
    transport_perm_sct = fields.Selection(related="vehicle_setup_id.transport_perm_sct", string='SCT Permit Type',
                                          help='The type of permit code to carry out the goods transfer service')
    sct_permit_number = fields.Char(related="vehicle_setup_id.name", index='trigram')
    transport_insurer = fields.Char(related="vehicle_setup_id.transport_insurer", index='trigram')
    transport_insurance_policy = fields.Char(related="vehicle_setup_id.transport_insurance_policy", index='trigram')
