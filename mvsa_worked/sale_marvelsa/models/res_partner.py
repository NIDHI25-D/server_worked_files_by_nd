# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
	_inherit = 'res.partner'

	address = fields.Text(string="Address", compute='_get_address')
	legal_person_id = fields.Many2one(comodel_name='legal.person', string='Legal Person')

	def _get_address(self):
		"""
			Author: siddharth.vasani@setuconsulting.com
			Date: 22/01/25
			Task: Migration to v18 from v16
			Purpose: set address format of address field.
		"""
		_logger.debug("Compute _get_address method start")
		for rec in self:
			address = ""
			address = "{0} {1} \n Col. {2} CP: {3}, {4} \n {5}".format(
				#self.name or '',
				rec.street_name or '',
				rec.street_number or '',
				#self.street_number2 or '',
				rec.l10n_mx_edi_colony or '',
				#self.l10n_mx_edi_locality,
				#self.l10n_mx_edi_locality_id.name,
				rec.zip or '',
				rec.city_id.name or '',
				#self.l10n_mx_edi_locality or '',
				rec.state_id.name or '',
				rec.country_id.name or '')

			rec.address = address
		_logger.debug("Compute _get_address method end")
