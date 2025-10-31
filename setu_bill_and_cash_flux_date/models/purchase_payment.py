from odoo import fields, models, api


class PurchasePayment(models.Model):
    _name = 'purchase.payment'
    _description = 'Purchase Payment'

    bill_id = fields.Many2one('bill.type')
    account_payment_term_id = fields.Many2one('account.payment.term')
    date_type = fields.Selection(string='Date Type',
                                 selection=[
                                     ('date_approve', 'Confirmation Date'),
                                     ('delivery_date', 'Delivery Date'),
                                     ('vendor_bill_date', 'Vendor Bill Date'),
                                     ('bl_date', 'BL Date'),
                                     ('bl_date_at_sight', 'BL Date at Sight'),
                                     ('date_planned', 'Expected Arrival'),
                                 ])
    operation_type = fields.Selection(string='Operation Type',
                                      selection=[
                                          ('add', 'Add'),
                                          ('subtract', 'Subtract')
                                      ])
    days_quantity = fields.Integer('Days Quantity')
    is_create_bill_draft = fields.Boolean('Create bill draft')
    is_vendor = fields.Boolean('Vendor')
    bill_reference = fields.Char('Bill reference')
