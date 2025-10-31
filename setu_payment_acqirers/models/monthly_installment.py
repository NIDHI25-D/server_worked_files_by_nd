from odoo import api, models, fields, tools, _


class MonthlyInstallment(models.Model):
    _name = 'monthly.installment'
    _description = "MonthlyInstallment"

    months = fields.Integer(string="Months")
    percentage = fields.Float(string="%")
    payment_acquirer_id = fields.Many2one('payment.provider')
    minimum_amount = fields.Float(string="Minimum Amount")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
