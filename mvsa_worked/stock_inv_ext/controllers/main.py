from odoo import http
from odoo.http import request
from odoo.addons.stock_barcode.controllers.stock_barcode import StockBarcodeController


class StockBarcodeControllerSupervisor(StockBarcodeController):

    def _get_groups_data(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 18/03/25
            Task: Migration to v18 from v16
            Purpose : add a group to the barcode to visible conditionality via group.
        """
        res = super()._get_groups_data()
        res.update({'group_stock_inventory_supervisor': request.env.user.has_group(
            'stock_inv_ext.group_stock_inventory_supervisor')})
        return res
