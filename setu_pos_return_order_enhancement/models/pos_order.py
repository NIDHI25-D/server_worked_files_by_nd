from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'


    returned_order_id = fields.Many2one(comodel_name='pos.order', string='Returned Order', readonly=True)


    def copy(self, default=None):
        """
          Author: jay.garach@setuconsulting.com
          Date: 17/12/24
          Task: Migration from V16 to V18
          Purpose: setting the return order id
        """
        self.ensure_one()
        order = super().copy(default=default)
        if self.env.context.get('refund', False):
            order.returned_order_id = self.id
        return order

    def refund(self):
        """
          Author: jay.garach@setuconsulting.com
          Date: 17/12/24
          Task: Migration from V16 to V18
          Purpose: Inherit method for break to create return of return order
        """
        # if already order is return with all order line and its all qty
        if self.returned_order_id:
            raise UserError(_("You can not create a return of return order."))
        get_previous_refund_orders = self.env['pos.order'].search(
            [('returned_order_id', '=', self.id)]).filtered(lambda x: x.state not in 'cancel')
        main_order_total_qty = sum(self.lines.mapped('qty'))
        refunded_orders_total_qty = abs(sum(get_previous_refund_orders.lines.mapped('qty')))
        # if order's each line qty fully refunded
        if main_order_total_qty <= refunded_orders_total_qty:
            raise UserError(
                _(f"You have already fully refunded this order named {get_previous_refund_orders[0].name}."))
        return super(PosOrder, self.with_context(refund=True)).refund()
