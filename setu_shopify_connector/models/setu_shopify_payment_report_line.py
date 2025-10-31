# -*- coding: utf-8 -*-
from odoo import models, fields


class SetuShopifyPaymentReportLine(models.Model):
    _name = "setu.shopify.payment.report.line"
    _description = "Shopify Payment Report Line"
    _rec_name = "transaction_id"

    is_processed = fields.Boolean(string="Is Processed?")
    is_remaining_statement = fields.Boolean(string="Is Remaining Statement?")

    transaction_id = fields.Char(string="Transaction ID")
    source_order_id = fields.Char(string="Order Reference ID")

    amount = fields.Float(string="Amount")
    fee = fields.Float(string="Fees")
    net_amount = fields.Float(string="Net Amount")

    transaction_type = fields.Selection([('charge', 'Charge'), ('refund', 'Refund'), ('dispute', 'Dispute'),
                                         ('reserve', 'Reserve'), ('adjustment', 'Adjustment'), ('credit', 'Credit'),
                                         ('debit', 'Debit'), ('payout', 'Payout'), ('payout_failure', 'Payout Failure'),
                                         ('payout_cancellation', 'Payout Cancellation'), ('fees', 'Fees'),
                                         ('payment_refund', 'Payment Refund')])

    source_type = fields.Selection([('charge', 'Charge'), ('refund', 'Refund'), ('dispute', 'Dispute'),
                                    ('reserve', 'Reserve'), ('adjustment', 'Adjustment'), ('payout', 'Payout')])

    shopify_payment_report_id = fields.Many2one('setu.shopify.payment.report', string="Payment ID", ondelete="cascade")
    currency_id = fields.Many2one('res.currency', string='Currency')
    order_id = fields.Many2one('sale.order', string="Order Reference")
