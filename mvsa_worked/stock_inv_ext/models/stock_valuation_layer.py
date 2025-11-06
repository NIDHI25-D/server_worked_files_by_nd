from odoo import fields, models, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    product_brand_id = fields.Many2one(comodel_name='product.brand',
                                       related='product_id.product_tmpl_id.product_brand_id', store=True)
    compatible_ids = fields.Many2many(related="product_id.compatible_ids", comodel_name='marvelfields.compatible',
                                      string='Compatibles')
    marca_ids = fields.Many2many(related="product_id.marca_ids", comodel_name='marvelmarcas.marca', string='Marcas Compatibles')