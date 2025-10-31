# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: set is_oversized as per sale_order_line
        """
        res = super(StockMove,self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        res.update({'is_oversized': self.product_id.is_oversized})
        return res

