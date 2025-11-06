from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    is_next_day_shipping = fields.Boolean(string="Next Day Shipping",
                                          readonly=True, default=False, copy=False)

