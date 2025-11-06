# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
from odoo.exceptions import ValidationError


class SetuEcommerceImportExportProcessWiz(models.TransientModel):
    _inherit = 'setu.ecommerce.import.export.process.wiz'

    ecommerce_operation_mirakl = fields.Selection(selection=[("import_specific_order", "Import Specific Order-IDS")],
                                                  string="Mirakl Operation")

    def mirakl_connector_ecommerce_perform_operation(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: performing an operation to create and sync sale order from mirakl connector.
        """
        setu_sale_order =  self.env["sale.order"]
        multi_ecommerce_connector_id = self.multi_ecommerce_connector_id

        if self.ecommerce_operation_mirakl == "import_specific_order":
            setu_sale_order.mirakl_create_import_specific_order_chain(multi_ecommerce_connector_id, self.import_specific_order_ids)

        return {"type": "ir.actions.client", "tag": "reload"}

