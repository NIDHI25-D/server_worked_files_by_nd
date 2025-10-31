# -*- coding: utf-8 -*-


from odoo import models, fields


class SetuShopifyRiskyOrder(models.Model):
    _name = "setu.shopify.risky.order"
    _description = 'Shopify Risky Order'
    _rec_name = "original_shopify_order_id"

    is_cause_cancel_order = fields.Boolean(string="Is Cause Cancel Order", default=False)

    risk_id = fields.Char(string="Risky Order ID")
    original_shopify_order_id = fields.Char(string="Original Shopify Order Belongs")
    source = fields.Char(string="Source Of Risky Order")

    message = fields.Text(string="Order Message", translate=True)
    recommendation_status = fields.Selection(
        [('cancel', 'The merchant should cancel the order.(High Level Order Fraudulent)'),
         ('investigate', 'The merchant should investigate the order (Medium Level Order Fraudulent)'),
         ('accept', 'The order risk found no indication of fraud.(Low Level Order Fraudulent)')],
        string='Recommendation', default='accept')

    sale_order_id = fields.Many2one("sale.order", string="Order")
