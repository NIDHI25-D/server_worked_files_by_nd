from odoo import models, fields,api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )

    crm_tags_ids = fields.Many2many('crm.tag', 'crm_id', 'tag_id', string="Product Tags")