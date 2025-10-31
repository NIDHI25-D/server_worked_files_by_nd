# -*- coding: utf-8 -*-
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_create_tms_shipment(self):
        """
            Author: jatin.babariya@setuconsulting.com
            Date: 20/03/25
            Task: Migration from V16 to V18.
            Purpose: to return a wizard from server action to create a shipment as per the task point - A in above url.
        """
        return {
            'name': 'Create TMS Shipment',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'create.tms.shipment.wiz'
        }
