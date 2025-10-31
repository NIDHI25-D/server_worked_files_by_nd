# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger("adding_ewallet_points_for_not_delivered_quantity")


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process_cancel_backorder(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
            Purpose: credit the partner E-wallet points based on non-delivered products.
        """
        pickings_ids = self.env.context.get('button_validate_picking_ids')
        if pickings_ids:
            pickings_ids = self.env['stock.picking'].browse(pickings_ids).filtered(
                lambda x: x.picking_type_code == 'outgoing')
            for pickings_id in pickings_ids:
                pickings_line_qty_difference_ids = pickings_id.mapped('move_ids_without_package').filtered(
                    lambda x: x.product_uom_qty != x.quantity)
                sale_order_id = pickings_id.sale_id
                sale_order_line_ids = sale_order_id.order_line.filtered(
                    lambda x: x.product_id.id in pickings_line_qty_difference_ids.product_id.ids)
                ewallet_line_ids = sale_order_id.order_line.filtered(
                    lambda x: x.reward_id.program_type == 'ewallet')
                if ewallet_line_ids:
                    ewallet_points_to_update = 0
                    for ewallet_line_id in ewallet_line_ids:
                        price_total_for_ewallet_points = 0
                        for pickings_line_qty_difference_id in pickings_line_qty_difference_ids:
                            pickings_line_qty_difference_id_with_same_tax_id = sale_order_line_ids.filtered(
                                lambda
                                    x: x.product_id.id == pickings_line_qty_difference_id.product_id.id and x.tax_id.ids == ewallet_line_id.tax_id.ids)
                            if pickings_line_qty_difference_id_with_same_tax_id:
                                discount = sale_order_id.order_line.reward_id.filtered(
                                    lambda x: x.program_id.program_type == "promotion").discount
                                total_amount = sum(
                                    pickings_line_qty_difference_id_with_same_tax_id.mapped('price_total'))
                                if discount:
                                    total_amount = total_amount - ((total_amount * discount) / 100)
                                total_quantity = sum(
                                    pickings_line_qty_difference_id_with_same_tax_id.mapped('product_uom_qty'))
                                difference_qty = sum(pickings_line_qty_difference_id.mapped(
                                    'product_uom_qty')) - pickings_line_qty_difference_id.quantity
                                if total_amount and total_quantity and difference_qty:
                                    price_total_for_ewallet_points += (total_amount * difference_qty) / total_quantity
                        sale_order_line_with_same_tax_price_total = sum(sale_order_id.order_line.filtered(lambda
                                                                                                              x: x.tax_id.ids == ewallet_line_id.tax_id.ids and x.reward_id.program_type != 'ewallet').mapped(
                            'price_total'))
                        ewallet_points_to_update += (-(
                                price_total_for_ewallet_points * ewallet_line_id.price_total) / sale_order_line_with_same_tax_price_total)
                    coupon_id = ewallet_line_ids.coupon_id
                    if coupon_id:
                        total_amount_to_update = round((coupon_id.points + ewallet_points_to_update), 2)
                        coupon_id.write({'points': total_amount_to_update})
                        coupon_id.message_post(body=_(
                            f"Amount of points {round(ewallet_points_to_update, 2)} added for this transfer {pickings_id.name}."))
        return super(StockBackorderConfirmation, self).process_cancel_backorder()
