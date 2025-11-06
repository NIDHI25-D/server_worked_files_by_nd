# -*- coding: utf-8 -*-

from odoo import models, fields

class TransportShipment(models.Model):
    _inherit = 'shipment.tracking'

    shipment_id = fields.Many2one(ondelete='cascade')