from odoo import models, fields,api

class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_tags = fields.Many2many(related='product_id.crm_tags_ids')