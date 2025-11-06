# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
	_inherit = "product.template"
	
	spare_parts_product_ids = fields.Many2many('product.template', 'product_spare_parts_rel', 'src_id', 'dest_id', string='Spare Parts')