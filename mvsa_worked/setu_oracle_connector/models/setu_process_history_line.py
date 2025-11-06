# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SetuProcessHistoryLine(models.Model):
    _inherit = "setu.process.history.line"

    setu_oracle_product_chain_line_id = fields.Many2one("setu.ecommerce.product.chain.line",
                                                        string="Oracle Product Chain Line")

    # def oracle_create_product_process_history_line(self, message, model_id, product_chain_line_id, process_history_id,
    #                                                sku=""):
    #     vals = self.oracle_prepare_process_history_line_vals(message, model_id, product_chain_line_id,
    #                                                          process_history_id)
    #     vals.update({'setu_oracle_product_chain_line_id': product_chain_line_id.id if product_chain_line_id else False,
    #                  "default_code": sku})
    #     process_history_line_id = self.create(vals)
    #     return process_history_line_id
    #
    # def oracle_create_sale_order_process_history_line(self, message, model_id, product_chain_line_id,
    #                                                   process_history_id,
    #                                                   sku=""):
    #     vals = self.oracle_prepare_process_history_line_vals(message, model_id, product_chain_line_id,
    #                                                          process_history_id)
    #     vals.update({'setu_oracle_product_chain_line_id': product_chain_line_id.id if product_chain_line_id else False,
    #                  "default_code": sku})
    #     process_history_line_id = self.create(vals)
    #     return process_history_line_id
    #
    # def oracle_create_attachment_process_history_line(self, message, model_id, product_chain_line_id,
    #                                                   process_history_id,
    #                                                   sku=""):
    #     vals = self.oracle_prepare_process_history_line_vals(message, model_id, product_chain_line_id,
    #                                                          process_history_id)
    #     vals.update({'setu_oracle_product_chain_line_id': product_chain_line_id.id if product_chain_line_id else False,
    #                  "default_code": sku})
    #     process_history_line_id = self.create(vals)
    #     return process_history_line_id
    #
    # def oracle_prepare_process_history_line_vals(self, message, model_id, record_id, process_history_id):
    #     vals = {'message': message, 'model_id': model_id, 'record_id': record_id.id if record_id else False,
    #             'process_history_id': process_history_id.id if process_history_id else False}
    #     return vals
