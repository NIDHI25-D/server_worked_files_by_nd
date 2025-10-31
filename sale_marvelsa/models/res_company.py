# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class res_company(models.Model):
	_inherit = "res.company"

	customer_agrobolder_id = fields.Many2one('res.partner', string="Customer Agrobolder")