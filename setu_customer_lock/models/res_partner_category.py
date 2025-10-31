from odoo import fields, models, api, _


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_customer_lock_reason = fields.Boolean("Is it for customer locking?",
                                             help="Set this True, if you want to lock this customer from creating a "
                                                  "sale order", default=False)
