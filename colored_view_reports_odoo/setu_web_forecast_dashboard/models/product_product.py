from odoo import models, fields,api

class ProductProduct(models.Model):
    _inherit = "product.product"

    def open_amz_margin(self):
        '''
        --To open the tree view of Amz Margin
        --Path : Product(any 1) -> AMZ Margin
        '''
        return {
            'type': 'ir.actions.act_window',
            'name': 'AMZ Margin',
            'res_model': 'forecast.report.amz.margin',
            'domain': [('amz_margin_product_id', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current',
        }
