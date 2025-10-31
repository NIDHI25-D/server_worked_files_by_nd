from odoo import api, fields, models


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_enable_for_create_bill = fields.Boolean('Enable for create bill?', default=False)
