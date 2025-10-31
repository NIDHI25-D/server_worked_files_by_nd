from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_oversized = fields.Boolean(string='Oversized',  readonly=True)
