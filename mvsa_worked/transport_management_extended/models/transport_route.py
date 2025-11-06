# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TransportRoute(models.Model):
    _inherit = 'transport.route'

    active = fields.Boolean('Active', default=True)
