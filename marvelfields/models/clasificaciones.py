# -*- coding: utf-8 -*-

from odoo import models, fields


class Clasificaciones(models.Model):
    _name = 'marvelfields.clasificaciones'
    _description = "Marvelfields Clasificaciones"

    name = fields.Char(required=True, string='Clasificacion')
    abreviatura = fields.Char(required=True, string='Abreviatura')
    color = fields.Integer('Color Index', default=0)
