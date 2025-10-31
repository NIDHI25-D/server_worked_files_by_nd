from odoo import models, api, fields


class PreorderSalePurchaseRel(models.Model):
    _name = "preorder.sale.purchase.rel"
    _description = "Preorder Sale Purchase connection"

    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase Order Line")
    sale_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    product_id = fields.Many2one("product.product", related="sale_line_id.product_id")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
    preorder_qty = fields.Float(string="Preorder Quantity")
    pre_order_state = fields.Selection(related='sale_id.state', store=True)

