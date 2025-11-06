from odoo import fields, models, api


class ResPartner(models.Model):

    _inherit = "res.partner"

    dealer_type = fields.Selection([('is_cash_dealer', 'Cash Dealer'), ('is_credit_dealer', 'Credit Dealer')],
                                   string="Dealer Type")
    requested_company_id = fields.Many2one('res.partner')