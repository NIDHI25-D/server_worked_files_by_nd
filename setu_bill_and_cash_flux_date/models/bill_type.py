from odoo import fields, models, api


class BillType(models.Model):
    _name = 'bill.type'
    _description = 'bill type'

    name = fields.Char(string='Bill Type')
    currency_id = fields.Many2one('res.currency')
    journal_id = fields.Many2one('account.journal')
    product_id = fields.Many2one('product.product')
    account_id = fields.Many2one('account.account')
    analytic_id = fields.Many2one('account.analytic.account')
    account_payment_term_id = fields.Many2one('account.payment.term')
    purchase_payment_id = fields.Many2one('purchase.payment')
    is_it_tax_type = fields.Boolean('Is it tax type?', default=False)
