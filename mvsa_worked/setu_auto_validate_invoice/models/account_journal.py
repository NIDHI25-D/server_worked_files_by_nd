from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_default_other_country = fields.Boolean('Is Default for Other Country', default=False,
                                              help='If true then this journal will be set invoice where '
                                                   'customer country is different then company country')