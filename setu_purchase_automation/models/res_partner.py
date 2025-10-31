from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    departure_shipment_ports_ids = fields.Many2many('loading.port.cateloges', string="departure / shipment ports")
