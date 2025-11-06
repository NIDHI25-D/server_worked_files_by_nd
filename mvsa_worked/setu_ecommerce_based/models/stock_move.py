# -*- coding: utf-8 -*-
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : This method will use to link ecommerce connector ref. in picking
        :return: dictionary
        """
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.multi_ecommerce_connector_id:
            res.update({'multi_ecommerce_connector_id': order_id.multi_ecommerce_connector_id.id})
        return res

    def _action_assign(self,force_qty=False):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : When reserve qty link ecommerce connector ref
        :param force_qty:
        :return:
        """
        res = super(StockMove, self)._action_assign(force_qty=force_qty)
        for picking_id in self.picking_id:
            if not picking_id.multi_ecommerce_connector_id and picking_id.sale_id and picking_id.sale_id.multi_ecommerce_connector_id:
                picking_id.write({'multi_ecommerce_connector_id': picking_id.sale_id.multi_ecommerce_connector_id.id})
        return res
