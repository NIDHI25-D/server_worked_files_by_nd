# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SetuProcessHistoryLine(models.Model):
    _name = "setu.process.history.line"
    _description = "Process History Line"

    # Char and Text fields
    order_ref = fields.Char(string='Order Reference', translate=True)
    default_code = fields.Char(string='SKU', translate=True)
    message = fields.Text(string="Message", translate=True)

    # Integer fields
    record_id = fields.Integer(string="Record ID")

    # Relational fields
    model_id = fields.Many2one(comodel_name="ir.model", string="Model")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    sale_order_id = fields.Many2one(comodel_name="sale.order", string="Sale Order")
    setu_ecommerce_product_chain_line_id = fields.Many2one(
        comodel_name="setu.ecommerce.product.chain.line",
        string="e-Commerce Product Chain Line")
    setu_ecommerce_order_chain_line_id = fields.Many2one(
        comodel_name="setu.ecommerce.order.chain.line",
        string="e-Commerce Order Chain Line")
    setu_ecommerce_customer_chain_line_id = fields.Many2one(
        comodel_name="setu.ecommerce.customer.chain.line",
        string="e-Commerce Customer Chain Line")
    process_history_id = fields.Many2one(
        comodel_name="setu.process.history",
        string="Process History", ondelete="cascade")

    @api.model
    def get_model_id(self, model_name):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to find model id based on name
        :param model_name:
        :return: model id or False
        """
        ir_mode_obj = self.env['ir.model']
        ir_model_id = ir_mode_obj.search([('model', '=', model_name)])
        if ir_model_id:
            return ir_model_id.id
        return False

    def create_process_history_line(self, message, model_id, record_id, process_history_id, default_code='',
                                    order_ref='', product_id=False):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to process history line
        :param message:
        :param model_id:
        :param record_id:
        :param process_history_id:
        :param default_code:
        :param order_ref:
        :param product_id:
        :return: process history record
        """
        vals = {'message': message,
                'default_code': default_code,
                'order_ref': order_ref,
                'product_id': product_id and product_id.id or False,
                'model_id': model_id,
                'record_id': record_id.id if record_id else False,
                'process_history_id': process_history_id.id if process_history_id else False}
        process_history_id = self.create(vals)
        return process_history_id
