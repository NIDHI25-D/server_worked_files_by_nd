# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class res_company(models.Model):
    _inherit = "res.company"

    kiosk_mode_logo = fields.Binary('Kiosk Mode Logo')
