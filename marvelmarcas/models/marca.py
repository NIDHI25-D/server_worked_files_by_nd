# -*- coding: utf-8 -*-

from odoo import models, fields


class Marca(models.Model):
    _name = 'marvelmarcas.marca'
    _description = 'marvelmarcas.marca'

    name = fields.Char(
        required=True,
        string='Marca',
    )
    color = fields.Integer('Color Index', default=0)
