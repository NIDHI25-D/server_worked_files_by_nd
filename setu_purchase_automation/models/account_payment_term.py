from odoo import api, fields, models


class AccountPaymentTerms(models.Model):
    _inherit = 'account.payment.term'

    payment_terms_uses = fields.Selection([('for_customer', 'is Customer payment term?'),
                                           ('for_vendor', 'is Vendor payment term?')],
                                          string="Payment terms uses", required=True, default='for_customer')
    apply_loc = fields.Boolean(string="Apply Letter of Credit?", default=False)
    credit_days_configure = fields.Integer("Credit Days")
