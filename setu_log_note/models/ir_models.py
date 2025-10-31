# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class IrModel(models.Model):
    _inherit = 'ir.model'

    is_tracked_module_field = fields.Boolean(
        string="Tracked",
        help="This field identifies if the fields in this models are being tracked"
    )