from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    loyalty_points = fields.Float(help='The amount of Loyalty points the customer won or lost with this order',
                                  copy=False)

    loyalty_points_redeemed = fields.Float(string="Redeemed Points",
                                           help='The number of Loyalty Points that the customer has redeemed for this '
                                                'order.', copy=False)
    points_before_order = fields.Float(string="Points before this order", copy=False)

    pp_order = fields.Float("Points Per Order", copy=False)
    is_customer_blocked = fields.Boolean(string="Customer blacklisted?", default=False, help="Is the customer "
                                                                                             "blacklisted at a time "
                                                                                             "of Order.", copy=False)
    returned_order_id = fields.Many2one(comodel_name='pos.order', string='Returned Order', readonly=True)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_product_blacklisted = fields.Boolean(string="Is Product Blacklisted?", default=False, copy=False)
    points_per_currency = fields.Float("Points Per Currency", copy=False, default=0)
    points_per_product = fields.Float("Points Per Product", copy=False, default=0)
