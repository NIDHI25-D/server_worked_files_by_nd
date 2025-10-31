# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields


class SetuProcessHistoryLine(models.Model):
    _inherit = "setu.process.history.line"

    setu_shopify_customer_chain_line_id = fields.Many2one("setu.ecommerce.customer.chain.line",
                                                          string="Shopify Customer Chain Line")
    setu_shopify_order_chain_line_id = fields.Many2one("setu.ecommerce.order.chain.line",
                                                       string="Shopify Order Chain Line")
    setu_shopify_product_chain_line_id = fields.Many2one("setu.ecommerce.product.chain.line",
                                                         string="Shopify Product Chain Line")
    setu_shopify_payment_report_line_id = fields.Many2one("setu.shopify.payment.report.line",
                                                          string="Shopify Payment Report")
