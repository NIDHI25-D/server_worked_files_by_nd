# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    is_oversized = fields.Boolean(string='Oversized', readonly=True)

    def _trigger_scheduler(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 22/01/25
            Task: Migration to v18 from v16
            Purpose: if no_auto_scheduler then return.
        """
        if self.env['ir.config_parameter'].sudo().get_param('stock.no_auto_scheduler'):
            return
        return super()._trigger_scheduler()
