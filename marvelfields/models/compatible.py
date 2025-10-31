# -*- coding: utf-8 -*-

from odoo import models, fields


class Compatible(models.Model):
    _name = 'marvelfields.compatible'
    _description = "Marvelfields Compatible"

    name = fields.Char(required=True, string='Compatible')
    color = fields.Integer('Color Index', default=0)
