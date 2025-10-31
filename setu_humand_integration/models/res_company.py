# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class res_company(models.Model):
    _inherit = "res.company"

    humand_access_token = fields.Char(string='Access Token')
    humand_default_password = fields.Char(string="Humand Default Password")
