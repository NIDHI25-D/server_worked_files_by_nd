from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_default_other_country = fields.Boolean('Is Default for Other Country', default=False,
                                              help='If true then this account will be set invoice where '
                                                   'customer country is different then company country')