# -*- coding: utf-8 -*-
from odoo import fields, models, api

class SaleMarvelsaResSetting(models.TransientModel): 
	_inherit = 'res.config.settings'

	customer_agrobolder_id = fields.Many2one(related='company_id.customer_agrobolder_id', readonly=False,
		string="Customer Agrobolder")