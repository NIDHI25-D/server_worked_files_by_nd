from odoo import api, fields, models

class Respartner(models.Model):
    _inherit = 'res.partner'

    is_urgent_order = fields.Boolean("Urgent order")
