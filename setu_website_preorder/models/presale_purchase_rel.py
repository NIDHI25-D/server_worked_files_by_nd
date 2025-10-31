from odoo import models, api, fields


class PreorderSalePurchaseRel(models.Model):
    _name = "presale.purchase.rel"
    _description = "Pre Sale Purchase connection"

    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase Order Line")
    sale_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    product_id = fields.Many2one("product.product", related="sale_line_id.product_id")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
    presale_qty = fields.Float(string="Presale Quantity")
    pre_sale_state = fields.Selection(related='sale_id.state', store=True)