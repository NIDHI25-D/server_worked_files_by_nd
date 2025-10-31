from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def _calculate_inventory_custom_number(self):
    #     """
    #         Author: harshit@setuconsulting.com
    #         Date: 12/05/23
    #         Task: Migration
    #         Purpose: This method used for attach the customs number in invoice lines.
    #                     1) Find the stock move line which has the remaining qty and location is 'inventory'.
    #                     2) Remaining Quantity's Calculation for decrease the quantity to the stock move line related to the type
    #                         of current move_type of invoice.
    #                     3) If stock move line has customs number then it will automatically set to the invoice lines.
    #     """
    #     for line in self.mapped('invoice_line_ids').filtered('sale_line_ids'):
    #         moves = line.mapped('sale_line_ids.move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped)
    #         inventory_move = self.env['stock.move.line'].search(
    #             [('product_id', '=', line.product_id.id), ('move_id.location_id.usage', '=', 'inventory'),
    #              ('location_dest_id', 'in', moves.move_line_ids.location_id.ids),
    #              ('company_id', '=', self.company_id.id), ('remaining_qty', '>=', 1)])
    #
    #         move_lines = []
    #         taken_qty = line.quantity
    #         if inventory_move and line.move_id.move_type == 'out_invoice':
    #             for move_line in inventory_move:
    #                 if move_line.remaining_qty >= taken_qty:
    #                     move_line.remaining_qty -= taken_qty
    #                     move_lines.append(move_line.id)
    #                     break
    #                 elif move_line.remaining_qty != 0 and move_line.remaining_qty < taken_qty:
    #                     taken_qty -= move_line.remaining_qty
    #                     move_line.remaining_qty -= move_line.remaining_qty
    #                     move_lines.append(move_line.id)
    #                     continue
    #         elif inventory_move and line.move_id.move_type == 'out_refund':
    #             for move_line in inventory_move:
    #                 move_line.remaining_qty += taken_qty
    #                 move_lines.append(move_line.id)
    #                 break
    #
    #         # original_move_line = self.env['stock.move.line'].search(
    #         #     [('id', 'in', move_lines), ('product_id', '=', line.product_id.id)])
    #         original_move_lines = self.env['stock.move.line'].browse(move_lines)
    #
    #         if not moves or not inventory_move or not original_move_lines:
    #             continue
    #
    #         customs_number = original_move_lines.filtered(lambda x: x.customs_number and x.product_id.id == line.product_id.id)
    #         if not customs_number:
    #             return True
    #
    #         if line.l10n_mx_edi_customs_number:
    #             line.l10n_mx_edi_customs_number += f", {','.join(list(set(customs_number.mapped('customs_number'))))}"
    #         else:
    #             line.l10n_mx_edi_customs_number = ','.join(list(set(customs_number.mapped('customs_number'))))
    #     return True
    #
    # def _post(self, soft=True):
    #     # res = super(AccountInvoice, self).action_post()
    #     for invoice in self:
    #         if invoice.partner_id.property_account_position_id.name != 'Foreign Customer':
    #             invoice._calculate_inventory_custom_number()
    #         else:
    #             if invoice.l10n_mx_edi_external_trade_type != '02':
    #                 invoice._calculate_inventory_custom_number()
    #     return super(AccountMove, self)._post(soft=soft)
