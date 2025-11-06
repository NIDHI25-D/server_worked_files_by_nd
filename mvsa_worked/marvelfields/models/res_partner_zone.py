# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartnerZone(models.Model):
    _name = "res.partner.zone"
    _description = "Res Partner Zone"

    name = fields.Char(string="Zone")
