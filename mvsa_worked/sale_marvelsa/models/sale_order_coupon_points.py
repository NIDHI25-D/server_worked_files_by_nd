from odoo import fields, models


class SaleOrderCouponPoints(models.Model):
    _inherit = 'sale.order.coupon.points'
    _rec_name = 'appiled_promotion_id'

    appiled_promotion_id = fields.Many2one('loyalty.program', related='coupon_id.program_id', store=True)
