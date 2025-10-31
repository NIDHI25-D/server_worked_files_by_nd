# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    password_expiration = fields.Integer(
        string="Days",
        related="company_id.password_expiration", readonly=False
    )
    password_minimum = fields.Integer(
        string="Minimum Hours",
        related="company_id.password_minimum", readonly=False
    )
    password_history = fields.Integer(
        string="History",
        related="company_id.password_history", readonly=False
    )
    password_lower = fields.Integer(
        string="Lowercase",
        related="company_id.password_lower", readonly=False
    )
    password_upper = fields.Integer(
        string="Uppercase",
        related="company_id.password_upper", readonly=False
    )
    password_numeric = fields.Integer(
        string="Numeric",
        related="company_id.password_numeric", readonly=False
    )
    password_special = fields.Integer(
        related="company_id.password_special", readonly=False
    )
