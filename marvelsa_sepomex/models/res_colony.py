# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class SepomexResColony(models.Model):
    _name = 'sepomex.res.colony'
    _description = 'sepomex.res.colony'
    _rec_name = "display_name"

    name = fields.Char(string="Colony")
    postal_code = fields.Char(string="Postal Code")
    city_id = fields.Many2one('res.city', string="City")

    display_name = fields.Char(compute='_compute_new_display_name',
                               store=True, index=True)

    @api.depends('postal_code', 'name', 'city_id', 'city_id.state_id', 'city_id.country_id')
    def _compute_new_display_name(self):
        _logger.debug("Compute _compute_new_display_name method start")
        for rec in self:
            name = [rec.postal_code if rec.postal_code else "", rec.name if rec.name else "",
                    rec.city_id.name if rec.city_id else ""]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            if rec.city_id.country_id:
                name.append(rec.city_id.country_id.name)
            rec.display_name = ", ".join(name)
        _logger.debug("Compute _compute_new_display_name method end")


class SepomexResColonyCSV(models.Model):
    _name = 'sepomex.res.colony.csv'
    _description = 'sepomex.res.colony.csv'

    postal_code = fields.Char()
    colony = fields.Char()
    l10n_mx_edi_city_id = fields.Char()
