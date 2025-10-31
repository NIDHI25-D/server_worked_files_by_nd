from odoo import api, fields, models, _


class PaymentPromotion(models.Model):
    _name = 'payment.promotion'
    _description = 'Payment Promotion'

    code = fields.Char('Code')
    name = fields.Char('name')

class PaymentOptions(models.Model):
    _name = 'payment.options'
    _description = 'Payment Options'

    code = fields.Char('Code')
    name = fields.Char('name')
