# -*- coding: utf-8 -*-
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector")
    ecommerce_connector = fields.Selection(
        related="multi_ecommerce_connector_id.ecommerce_connector",
        string="e-Commerce Connector", store=True)

    def _action_done(self):
        """
        @name : Kamlesh Singh
        @date : 29/10/2024
        @purpose : This method will use to process validate invoice and create payment
                   if configure is create invoice in sale workflow automation
        :return: True
        """
        result = super(StockPicking, self)._action_done()
        for picking in self:
            if picking.sale_id.invoice_status == 'invoiced':
                continue
            sale_order_automation_id = picking.sale_id and picking.sale_id.setu_sale_order_automation_id
            delivery_lines = picking.move_line_ids.filtered(lambda l: l.product_id.invoice_policy == 'delivery')
            if sale_order_automation_id and delivery_lines and sale_order_automation_id.is_create_invoice and picking.picking_type_id.code == 'outgoing':
                picking.sale_id.validate_invoice_create_payment(sale_order_automation_id)
        return result
