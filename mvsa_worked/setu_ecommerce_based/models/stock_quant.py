# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    is_ecommerce_inventory_adjustment = fields.Boolean(
        string="Is eCommerce Inventory Adjustment", default=False)
    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector", copy=False)

    ecommerce_connector = fields.Selection(
        related="multi_ecommerce_connector_id.ecommerce_connector",
        string="e-Commerce Connector", store=True)

    @api.model
    def _get_inventory_fields_write(self):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : user can edit when he want to edit a quant in `inventory_mode`.
        :return: list of fields
        """
        fields = super(StockQuant, self)._get_inventory_fields_write()
        fields += ['is_ecommerce_inventory_adjustment', 'multi_ecommerce_connector_id']
        return fields

    @api.model
    def create_ecommerce_stock_inventory(self, products, location_id, is_auto_validate_inventory=False):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : This method will use to create stock quant or update stock quant
        :param products:
        :param location_id:
        :param is_auto_validate_inventory:
        :return: list
        """
        stock_quant_lst = []
        for product_dict in products:
            if product_dict.get('product_id') and product_dict.get('product_qty'):
                existing_stock_quant_id = self.search([
                    ('location_id', '=', location_id.id),
                    ('product_id', '=', product_dict.get('product_id').id)], limit=1)
                if existing_stock_quant_id:
                    existing_stock_quant_id.write({"inventory_quantity": product_dict.get('product_qty')})

                if not existing_stock_quant_id:
                    existing_stock_quant_id = self.create({
                        'company_id': self.company_id.id,
                        "product_id": product_dict.get('product_id').id,
                        'location_id': location_id.id,
                        "inventory_quantity": product_dict.get('product_qty'),
                        'product_uom_id': product_dict.get('product_id').uom_id.id if product_dict.get(
                            'product_id').uom_id else False})
                if existing_stock_quant_id:
                    stock_quant_lst.append(existing_stock_quant_id.id)
        if stock_quant_lst and is_auto_validate_inventory:
            for stock_quant_id in stock_quant_lst:
                stock_quant_id = self.browse(stock_quant_id)
                stock_quant_id.action_apply_inventory()
        return stock_quant_lst
