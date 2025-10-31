from odoo import fields, models, api


class ResPartnerExt(models.Model):
    _inherit = "res.partner"

    disable_inv_automatic_sign = fields.Boolean(
        string='Disable Invoice Automatically signed',
        help="Check this to disable automatically sign invoice for this customer")