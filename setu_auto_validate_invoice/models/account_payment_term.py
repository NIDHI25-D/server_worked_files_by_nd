from odoo import models, fields, api, _


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    payment_way_id = fields.Many2one('l10n_mx_edi.payment.method', string='Payment Way')
