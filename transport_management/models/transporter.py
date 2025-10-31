# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class TransporterDetails(models.Model):
    """Transporter Details"""
    _name = 'transporter.details'
    _description = __doc__
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'format.address.mixin']

    active = fields.Boolean(default=True)
    color = fields.Integer('Color Index', default=0)
    name = fields.Char(string="Name", required=True)
    avatar = fields.Binary(string="Avatar")
    partner_id = fields.Many2one('res.partner', string="Contact")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    # Address Details
    street = fields.Char(related="partner_id.street")
    street2 = fields.Char(related="partner_id.street2")
    zip = fields.Char(related="partner_id.zip")
    city = fields.Char(related="partner_id.city")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               related="partner_id.state_id", domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 related="partner_id.country_id")

    delivery_type_ids = fields.Many2many('delivery.type', string="Delivery Type")
    note = fields.Html(string="Note")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    transport_charge = fields.Monetary('Transport Charges', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one("res.currency", string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, readonly=True)

    vehicle_count = fields.Integer(compute="_compute_count_all")
    shipment_count = fields.Integer(compute="_compute_count_all")

    def get_transporter_fleets(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to call action and open tree, form view by clicking Vehicles button.
        """
        self.ensure_one()
        domain = [('transporter_id', '=', self.id)]
        return {
            'name': _('Transport Vehicles'),
            'res_model': 'fleet.vehicle',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'context': {'create':False},
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'list'
        }

    def get_transport_shipment(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: to call action and open tree, form view by clicking Shipments button.
        """
        self.ensure_one()
        domain = [('transporter_id', '=', self.id)]
        return {
            'name': _('Shipment Orders'),
            'res_model': 'transport.shipment',
            'domain': domain,
            'type': 'ir.actions.act_window',
            'context': {'create':False},
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'list'
        }

    # compute methods
    def _compute_count_all(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: Compute Count All.
        """
        fleet_vehicle = self.env['fleet.vehicle'].sudo()
        shipment_order = self.env['transport.shipment'].sudo()
        for record in self:
            record.vehicle_count = fleet_vehicle.search_count([('transporter_id', '=', record.id)])
            record.shipment_count = shipment_order.search_count([('transporter_id', '=', record.id)])

    # onchange methods
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: Onchange Partner set phone, mobile and email..
        """
        for rec in self:
            rec.phone = rec.partner_id.phone
            rec.mobile = rec.partner_id.mobile
            rec.email = rec.partner_id.email


class DeliveryType(models.Model):
    """delivery type"""
    _name = 'delivery.type'
    _description = __doc__

    color = fields.Integer('Color Index', default=0)
    name = fields.Char(string="Delivery Type", required=True)
