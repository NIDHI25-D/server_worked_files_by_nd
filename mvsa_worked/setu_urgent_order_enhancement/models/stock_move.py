from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 10/01/25
            Task: Migration from V16 to V18
            Purpose:
        """
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.group_id.sale_id
        res.update({'urgent_order': order_id.is_urgent_order})
        return res
