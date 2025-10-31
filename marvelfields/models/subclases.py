# -*- coding: utf-8 -*-

from odoo import models, fields


class Subclases (models.Model):
    _name = 'marvelfields.subclases'
    _description = "Marvelfields Subclases"

    name = fields.Char(required=True,string='Subclase')
    abreviatura = fields.Char(required=True,string='Abreviatura')
    color = fields.Integer('Color Index', default=0)
