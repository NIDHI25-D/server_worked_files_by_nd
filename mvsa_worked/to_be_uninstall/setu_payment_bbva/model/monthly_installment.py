from odoo import api, models, fields, tools, _


class MonthlyInstallment(models.Model):
    _inherit = 'monthly.installment'

    payment_promotion_id = fields.Many2one('payment.promotion', string='Payment Promotion')
    payment_options_ids = fields.Many2many('payment.options', 'acquirer_options_rel', 'month_id', 'option_id',
                                           string="Payment Options")