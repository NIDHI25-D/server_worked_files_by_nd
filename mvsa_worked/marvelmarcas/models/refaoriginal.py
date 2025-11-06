# -*- coding: utf-8 -*-

from odoo import models, fields


class Refaoriginal(models.Model):
    _name = 'marvelmarcas.refaoriginal'
    _description = 'marvelmarcas.refaoriginal'

    name = fields.Char(
        required=True,
        string='Refaccion Original',
    )

    color = fields.Integer('Color Index', default=0)
