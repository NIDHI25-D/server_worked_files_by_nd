# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportLocation(models.Model):
    """Transport Location"""
    _name = 'transport.location'
    _description = __doc__

    name = fields.Char(string="Location Name", required=True)
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    # address
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')


class TransportRoute(models.Model):
    """Transport Route"""
    _name = 'transport.route'
    _description = __doc__

    name = fields.Char(string="Route Name", required=True)
    # Source Location
    source_location_id = fields.Many2one('transport.location', string="Source Location", required=True)
    source_street = fields.Char(related="source_location_id.street", string=" Street")
    source_street2 = fields.Char(related="source_location_id.street2", string="Street 2")
    source_zip = fields.Char(related="source_location_id.zip", string=" ZIP")
    source_city = fields.Char(related="source_location_id.city", string=" City")
    source_state_id = fields.Many2one("res.country.state", string=' State', ondelete='restrict',
                                      related="source_location_id.state_id",
                                      domain="[('country_id', '=?', source_country_id)]")
    source_country_id = fields.Many2one('res.country', string=' Country', ondelete='restrict',
                                        related="source_location_id.country_id")
    # Destination Location
    destination_location_id = fields.Many2one('transport.location', string="Destination Location", required=True)
    destination_street = fields.Char(related="destination_location_id.street", string="Street")
    destination_street2 = fields.Char(related="destination_location_id.street2", string="Street2")
    destination_zip = fields.Char(related="destination_location_id.zip", string="ZIP")
    destination_city = fields.Char(related="destination_location_id.city", string="City")
    destination_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                           related="destination_location_id.state_id",
                                           domain="[('country_id', '=?', destination_state_id)]")
    destination_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                             related="destination_location_id.country_id")

    distance = fields.Float(string="Distance")
    transport_time = fields.Float(string="Estimation Time")
    transporter_ids = fields.Many2many('transporter.details', string="Transporters")

    @api.constrains('source_location_id', 'destination_location_id')
    def _check_source_destination_location(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: Check source and destination location, # if source location and destination location both are same then raise thia validation error.
        """
        for rec in self:
            if rec.source_location_id and rec.destination_location_id and rec.source_location_id.id == rec.destination_location_id.id:
                raise ValidationError(_("Source location and destination location cannot be the same.\nPlease change any one location."))
