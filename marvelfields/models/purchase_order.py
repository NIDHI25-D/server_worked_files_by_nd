from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    email_cc = fields.Char(string="Email Cc")
    is_ci = fields.Boolean(string='CI')
    is_pl = fields.Boolean(string='PL')
    is_telex = fields.Boolean(string='TELEX')
    is_mbl = fields.Boolean(string='MBL')
    is_notified = fields.Boolean(string='Notified')
    is_proforma = fields.Boolean(string='P.Proforma')
    is_cot_imp = fields.Boolean(string='Cot.IMP')
    is_revalidate = fields.Boolean(string='Revalidate')
    comments = fields.Text(string='Comments')
