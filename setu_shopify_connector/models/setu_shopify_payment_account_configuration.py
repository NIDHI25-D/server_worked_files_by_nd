# -*- coding: utf-8 -*-

from odoo import models, fields


class SetuShopifyPaymentAccountConfiguration(models.Model):
    _name = "setu.shopify.payment.account.configuration"
    _description = "Shopify Account Configurations"

    transaction_type = fields.Selection([('charge', 'Charge'), ('refund', 'Refund'), ('dispute', 'Dispute'),
                                         ('reserve', 'Reserve'), ('adjustment', 'Adjustment'), ('credit', 'Credit'),
                                         ('debit', 'Debit'), ('payout', 'Payout'), ('payout_failure', 'Payout Failure'),
                                         ('payout_cancellation', 'Payout Cancellation'), ('fees', 'Fees'),
                                         ('payment_refund', 'Payment Refund')], string="Transaction Type")

    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector')
    account_id = fields.Many2one('account.account', string="Account", help="The account used for this invoice.")
