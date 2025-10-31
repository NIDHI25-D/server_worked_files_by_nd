from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 01/01/25
            Task: Migration from V16 to V18
            Purpose: Set x_studio_detener_factura fields in the stock_picking according to set dfactura fields in the sale order.
        """
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.dfactura:
            res.update({'x_studio_detener_factura': True})
        return res
