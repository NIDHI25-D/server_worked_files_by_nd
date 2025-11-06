from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = "delivery.carrier"

    is_next_day_shipping = fields.Boolean(string="Next Day Shipping",
                                          default=False, copy=False)