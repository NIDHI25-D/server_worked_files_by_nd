from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    intial_order_quantity = fields.Float(default=0.0, string="Intial Order Quantity")

    @api.model_create_multi
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 10/03/25
            Task: Migration to v18 from v16
            Purpose: set the field Intial Order Quantity as a product_uom_qty during creation.
        """
        for val in vals:
            product_uom_quantity = val.get('product_uom_qty')
            if product_uom_quantity:
                val.update({'intial_order_quantity': product_uom_quantity})
        return super(StockMove, self).create(vals)
