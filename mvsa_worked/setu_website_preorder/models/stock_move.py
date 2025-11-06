from odoo import models, api, fields,_

class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose:To set current date in field : assortment_end_date when transfer is validate.
        """
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id:
            res.update({'is_preorder': order_id.is_preorder,
                        'is_presale': order_id.is_presale})
        return res
