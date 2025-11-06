from odoo import models, fields, api, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_promotion = fields.Boolean(string="Is Promotion ?")
    journal_id = fields.Many2one('account.journal', string='Journal')
