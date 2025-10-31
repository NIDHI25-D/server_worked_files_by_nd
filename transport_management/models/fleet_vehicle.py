# -*- coding: utf-8 -*-
# Copyright 2020-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    """Fleet Vehicle"""
    _inherit = 'fleet.vehicle'
    _description = __doc__

    transporter_id = fields.Many2one('transporter.details', string="Transporter")


class ResPartner(models.Model):
    """Res Partner"""
    _inherit = 'res.partner'
    _description = __doc__

    is_driver = fields.Boolean(string="Driver")
    is_transporter = fields.Boolean(string="Transporter")

    driver_license = fields.Char(string="License ID")
    license_type = fields.Char()
    days_to_expire = fields.Integer(compute='_compute_days_to_expire')
    license_valid_from = fields.Date()
    license_expiration = fields.Date()

    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Compute days to expire.
        """
        for rec in self:
            date = fields.Date.context_today(self)
            if rec.license_expiration:
                date = rec.license_expiration
            now = fields.Date.context_today(self)
            delta = date - now
            rec.days_to_expire = delta.days if delta.days > 0 else 0

    @api.constrains('license_expiration', 'license_valid_from')
    def _check_licence_expiration(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 21/03/25
            Task: Migration from V16 to V18.
            Purpose: To Check Licence Expiration.
        """
        for rec in self:
            if rec.license_valid_from and rec.license_expiration and rec.license_expiration < rec.license_valid_from:
                raise ValidationError(_("The licence expiration date cannot be earlier than licence valid date "))
