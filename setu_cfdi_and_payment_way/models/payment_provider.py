from odoo import models, fields, _


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    l10n_mx_edi_payment_method_id = fields.Many2one(
        comodel_name="l10n_mx_edi.payment.method",
        string='Payment Way',
        tracking=True)