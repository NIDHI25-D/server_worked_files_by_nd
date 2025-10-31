# -*- coding: utf-8 -*-
from odoo import models, fields


class MarcasStock(models.Model):
    _inherit = "product.template"

    marca_ids = fields.Many2many(
        'marvelmarcas.marca', 'marvelmarcas_marca_rel',
        'marcasrc_id', 'marcadest_id',
        string='Marcas Compatibles')


class RefaccionOriginalStock(models.Model):
    _inherit = "product.template"

    refaoriginal_ids = fields.Many2many(
        'marvelmarcas.refaoriginal', 'marvelmarcas_refaoriginal_rel',
        'refaoriginalsrc_id', 'refaoriginaldest_id',
        string='Refaccion Original')
