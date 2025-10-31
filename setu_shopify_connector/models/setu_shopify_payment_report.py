# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

from .. import shopify


class SetuShopifyPaymentReport(models.Model):
    _name = "setu.shopify.payment.report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Shopify Payment Report"
    _order = 'id desc'

    is_skip_from_cron = fields.Boolean(string="Skip From Schedule Actions", default=False)
    name = fields.Char(translate=True)

    payment_reference_id = fields.Char(string="Payment Reference ID")

    payment_date = fields.Date(string="Payment Date")

    amount = fields.Float(string="Total Amount")

    state = fields.Selection(
        [('draft', 'Draft'), ('partially_generated', 'Partially Generated'), ('generated', 'Generated'),
         ('partially_processed', 'Partially Processed'), ('processed', 'Processed'), ('validated', 'Validated')],
        string="Status", default="draft", tracking=True)
    payment_status = fields.Selection(
        [('scheduled', 'Scheduled'), ('in_transit', 'In Transit'), ('paid', 'Paid'), ('failed', 'Failed'),
         ('cancelled', 'Cancelled')])

    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency')
    statement_id = fields.Many2one('account.bank.statement', string="Bank Statement")
    process_history_id = fields.Many2one("setu.process.history", string="Process History")

    process_history_line_ids = fields.One2many(related="process_history_id.process_history_line_ids")
    shopify_payment_report_line_ids = fields.One2many('setu.shopify.payment.report.line', 'shopify_payment_report_id',
                                                      string="Payment Report Lines")