# -*- coding: utf-8 -*-


from odoo import models, fields, api


class SetuShopifySaleOrderProcessConfiguration(models.Model):
    _name = "setu.shopify.sale.order.process.configuration"
    _description = 'Sale auto workflow configuration'

    @api.model
    def _get_default_account_payment_terms(self):
        immediate_payment_terms_id = self.env.ref("account.account_payment_term_immediate")
        return immediate_payment_terms_id and immediate_payment_terms_id.id or False

    active = fields.Boolean(string="Active", default=True)

    shopify_order_financial_status = fields.Selection(
        [('pending', 'The payments are pending'), ('authorized', 'The payments have been authorized'),
         ('partially_paid', 'The order has been partially paid'), ('paid', 'The payments have been paid'),
         ('partially_refunded', 'The payments have been partially refunded'),
         ('refunded', 'The payments have been refunded'),
         ('voided', 'The payments have been voided')], default="paid")

    account_payment_term_id = fields.Many2one('account.payment.term', string='Payment Term',
                                              default=_get_default_account_payment_terms)
    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector')
    setu_shopify_payment_gateway_id = fields.Many2one("setu.shopify.payment.gateway", string="Shopify Payment Gateway",
                                                      ondelete="restrict")
    setu_sale_order_automation_id = fields.Many2one("setu.sale.order.automation", string="WorkFlow Automation")
