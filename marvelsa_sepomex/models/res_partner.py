# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    postal_code_id = fields.Many2one('sepomex.res.colony', string="Postal Code")

    @api.onchange('postal_code_id')
    def _onchange_postal_code_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/12/24
            Task: Migration from V16 to V18
            Purpose: set an address as per the postal_code
        """
        if self.postal_code_id:
            self.city = self.postal_code_id.city_id.name
            self.city_id = self.postal_code_id.city_id
            self.state_id = self.postal_code_id.city_id.state_id
            self.l10n_mx_edi_colony = self.postal_code_id.name
            self.l10n_mx_edi_locality = self.postal_code_id.city_id.state_id.name
            self.zip = self.postal_code_id.postal_code

    @api.onchange('city_id')
    def _onchange_city_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/12/24
            Task: Migration from V16 to V18
            Purpose: Set a zipcode as per the postal_code (https://app.clickup.com/t/865cgv7zv)
        """
        if self.postal_code_id:
            self.zip = self.postal_code_id.postal_code
