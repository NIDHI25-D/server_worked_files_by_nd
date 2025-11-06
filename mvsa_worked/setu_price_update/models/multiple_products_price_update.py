from odoo import models, fields, api, _

class Multipleproductsforpriceupdate(models.TransientModel):
    _name = 'multiple.products.price.update'
    _description = 'multiple.products.price.update'

    product_ids = fields.Many2many('product.product')

    @api.onchange('product_ids')
    def onchange_product_ids(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: This method apply the domain to display only those products which have competition level less than equal to competition level of price level config
                     return:
        """
        config = self.env['price.level.config'].browse(self._context.get('active_id'))
        return {'domain': {
            'product_ids': [('product_tmpl_id.competition_level_id.level', '<=', config.level_id.level),
                            ('id', 'not in', config.product_level_ids.mapped('product_id').ids)]}}

    def create_items(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Task: Migration to v18 from v16
            Purpose: To create the level of selected products
                     return:
        """
        price_level_config = self.env['price.level.config'].browse(self._context.get('active_id'))
        for prod in self.product_ids:
            price_level_config.write({'product_level_ids': [(0, 0, {'product_id': prod.id})]})
