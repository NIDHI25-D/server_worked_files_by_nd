from odoo import api, fields, models


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    purchase_payment_ids = fields.One2many('purchase.payment', 'account_payment_term_id', string='Purchase Payments')
