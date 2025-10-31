from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    def copy(self, vals):
        """
              Author: jay.garach@setuconsulting.com
              Date: 17/12/24
              Task: Migration from V16 to V18
              Purpose: This method is used for refund the order and manage its quantity
        """
        get_previous_refund_orders = self.env['pos.order'].search(
            [('returned_order_id', '=', self.order_id.id)]).filtered(lambda x: x.state not in 'cancel')
        # if current order having refund order
        if get_previous_refund_orders:
            # get return order line having match to current order line with previous order line
            returned_line = get_previous_refund_orders.lines.filtered(lambda x: x.product_id.id == self.product_id.id)
            # if current order qty is greater then already return product qty
            if self.qty > abs(sum(returned_line.mapped('qty'))):
                total_qty = self.qty - abs(sum(returned_line.mapped('qty')))
                total_price_sub_total = self.price_subtotal - abs(sum(returned_line.mapped('price_subtotal')))
                total_price_subtotal_incl = self.price_subtotal_incl - abs(
                    sum(returned_line.mapped('price_subtotal_incl')))
                if not total_qty:
                    return
                vals.update({
                    'qty': -total_qty,
                    'price_subtotal': -total_price_sub_total,
                    'price_subtotal_incl': -total_price_subtotal_incl,
                })
            # if current order line qty == returned order line qty
            elif self.qty == abs(sum(returned_line.mapped('qty'))):
                return
        super_request = super(PosOrderLine, self).copy(vals)
        pos_order = self.env['pos.order'].browse(int(vals.get('order_id')))
        pos_order._onchange_amount_all()
        return super_request

    @api.onchange('price_unit', 'tax_ids', 'qty', 'discount', 'product_id')
    def _onchange_amount_line_all(self):
        res = super(PosOrderLine, self)._onchange_amount_line_all()
        self.order_id._onchange_amount_all()
        get_previous_return_order = self.env['pos.order'].search(
            [('returned_order_id', '=', self.order_id.returned_order_id.id), ('id', '!=', self._origin.order_id.id)])
        get_previous_order_qty_count = sum(
            get_previous_return_order.lines.filtered(lambda x: x.product_id.id == self.product_id.id).mapped('qty'))
        total_remaining = self._origin.order_id.returned_order_id.lines.filtered(
            lambda p: p.product_id.id == self.product_id.id).qty + get_previous_order_qty_count
        # if qty greater than or equal 0
        if self.qty >= 0:
            raise UserError(_(f"Please apply negative stock for return."))
        #  if qty is greater than total remain qty
        if abs(self.qty) > abs(total_remaining):
            raise UserError(_(f"Only {total_remaining} available in refund for product {self.product_id.name}."))
        else:
            return {}
