# -*- coding: utf-8 -*-
from odoo import models, fields


class SetuEcommerceProductExportWiz(models.TransientModel):
    _name = 'setu.ecommerce.product.export.wiz'
    _description = 'eCommerce Product Export Wiz'

    basic_details = fields.Boolean(string='Basic Details')
    price_export = fields.Boolean(string='Price Export')
    set_image = fields.Boolean(string="Set Image")
    inventory_export = fields.Boolean(string='Inventory Export')

    export_action = fields.Selection(
        selection=[('create_and_sync', 'Create and Sync'), ('sync_only', 'Sync Only')],
        default='create_and_sync', string="Export Action", )

    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector", copy=False)

    def prepare_product_export_to_ecommerce(self):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : This method will use to prepare product to export ecommerce
        :return: True
        """
        if hasattr(self,
                   '%s_prepare_product_export_to_ecommerce' % self.multi_ecommerce_connector_id.ecommerce_connector):
            getattr(self,
                    '%s_prepare_product_export_to_ecommerce' % self.multi_ecommerce_connector_id.ecommerce_connector)()
        return True
