# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    password_expiration = fields.Integer(
        string="Days",
        default=60,
        help="How many days until passwords expire",
    )
    password_lower = fields.Integer(
        string="Lowercase",
        default=1,
        help="Require number of lowercase letters",
    )
    password_upper = fields.Integer(
        string="Uppercase",
        default=1,
        help="Require number of uppercase letters",
    )
    password_numeric = fields.Integer(
        string="Numeric",
        default=1,
        help="Require number of numeric digits",
    )
    password_special = fields.Integer(
        string="Special",
        default=1,
        help="Require number of unique special characters",
    )
    password_history = fields.Integer(
        string="History",
        default=30,
        help="Disallow reuse of this many previous passwords - use negative "
        "number for infinite, or 0 to disable",
    )
    password_minimum = fields.Integer(
        string="Minimum Hours",
        default=24,
        help="Amount of hours until a user may change password again",
    )
