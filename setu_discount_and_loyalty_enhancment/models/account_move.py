from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: jay.garach@setuconsulting.com
            Date: 16/12/23
            Task: Migration from V16 to V18
           Purpose: discount line set as per invoiced quantity
        """
        res = super().create(vals_list)
        for invoice in res:
            sale_order_id = invoice.invoice_line_ids.sale_line_ids.order_id
            if sale_order_id and invoice.move_type in ('out_invoice', 'out_refund'):
                reward_line_ids = invoice.invoice_line_ids.sale_line_ids.filtered(lambda x: x.is_reward_line)
                if reward_line_ids:
                    sale_reward_lines = sale_order_id.order_line.filtered(lambda x: x.is_reward_line)
                    value = []
                    for line in sale_reward_lines:
                        if line.reward_id.program_id.program_type == 'promotion' and line.reward_id.program_id.need_to_exclude_from_automatic_sign and line.reward_id.discount:
                            discount = line.reward_id.discount
                            discountable = 0
                            invoice_line_ids = invoice.invoice_line_ids.filtered(
                                lambda
                                    x: not x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.product_type == "consu" and x.product_id.is_storable)
                            if invoice_line_ids:
                                for invoice_line in invoice_line_ids:
                                    discountable += invoice_line.price_unit * invoice_line.quantity * (
                                            1 - (invoice_line.discount or 0.0) / 100.0)
                                # sum_of_quantity = sum(invoice_line_ids.mapped('quantity'))
                                unit_price_of_reward_line = round((round(discountable, 2) * discount) / 100, 2)
                                line_to_update = invoice.invoice_line_ids.filtered(lambda
                                                                                       x: x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.reward_id.id == line.reward_id.id)
                                if line_to_update:
                                    line_to_update.price_unit = -(unit_price_of_reward_line)
                                else:
                                    value.append((0, 0, {'product_id': line.product_id.id,
                                                         'price_unit': -(unit_price_of_reward_line),
                                                         'tax_ids': [(4, tax_id) for tax_id in line.tax_id.ids],
                                                         'is_reward_line': True,
                                                         'reward_id': line.reward_id.id})
                                                 )
                            else:
                                line_to_unlink = invoice.invoice_line_ids.filtered(
                                    lambda
                                        x: x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.reward_id.id == line.reward_id.id)
                                if line_to_unlink:
                                    line_to_unlink.unlink()
                    if value:
                        invoice.write({'invoice_line_ids': value})
                    if sale_order_id and invoice.move_type == 'out_invoice':
                        value = []
                        for line in sale_reward_lines:
                            if line.reward_id.program_id.program_type == 'ewallet':
                                delivery_line_id = sale_order_id.order_line.filtered(
                                    lambda x: x.is_delivery and x.tax_id.ids == line.tax_id.ids)
                                invoiced_delivery_line_id = invoice.invoice_line_ids.filtered(lambda
                                                                                                  x: x.product_id == delivery_line_id.product_id and x.tax_ids.ids == delivery_line_id.tax_id.ids)
                                invoice_line_ids = invoice.invoice_line_ids.filtered(
                                    lambda
                                        x: x.tax_ids.ids == line.tax_id.ids and not x.reward_id.program_id.program_type == "ewallet")
                                if invoiced_delivery_line_id and invoice_line_ids:
                                    if invoiced_delivery_line_id.id not in invoice_line_ids.ids:
                                        invoice_line_ids += invoiced_delivery_line_id
                                else:
                                    if invoiced_delivery_line_id:
                                        invoice_line_ids = invoiced_delivery_line_id
                                sale_order_line_product_same_taxes_ids = sale_order_id.order_line.filtered(
                                    lambda
                                        x: x.tax_id.ids == line.tax_id.ids and not x.reward_id.program_id.program_type == "ewallet")
                                if invoice_line_ids and sale_order_line_product_same_taxes_ids:
                                    invoice_lines_price_total = sum(invoice_line_ids.mapped('price_total'))
                                    sale_order_lines_price_total = sum(
                                        sale_order_line_product_same_taxes_ids.mapped('price_total'))
                                    if invoice_lines_price_total and sale_order_lines_price_total:
                                        price_total_for_ewallet_line = (
                                                                               invoice_lines_price_total * line.price_total) / sale_order_lines_price_total
                                        tax_amount_total = 0
                                        for tax_id in line.tax_id:
                                            if tax_id.children_tax_ids:
                                                for children_tax_id in tax_id.children_tax_ids:
                                                    if (
                                                            not children_tax_id.price_include or children_tax_id.include_base_amount):
                                                        tax_amount_total += children_tax_id.amount
                                                continue
                                            if (not tax_id.price_include or tax_id.include_base_amount):
                                                tax_amount_total += tax_id.amount
                                        price_unit_for_ewallet_line = (
                                                (price_total_for_ewallet_line * 100) / (100 + tax_amount_total))
                                        if (taxes_ids := [tax for tax in line.tax_id if tax.include_base_amount]
                                                         or [child_tax for child_tax in line.tax_id.children_tax_ids if
                                                             child_tax.include_base_amount]):
                                            total_void_amount = 0
                                            for taxes_id in taxes_ids:
                                                if taxes_id.price_include:
                                                    total_void_amount += taxes_id.amount
                                                else:
                                                    continue
                                            price_unit_for_ewallet_line = (
                                                (price_unit_for_ewallet_line * (1.0 + total_void_amount / 100.0)))
                                        line_to_update = invoice.invoice_line_ids.filtered(
                                            lambda
                                                x: x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.reward_id.id == line.reward_id.id)
                                        if line_to_update:
                                            line_to_update.price_unit = price_unit_for_ewallet_line
                                        else:
                                            value.append((0, 0, {'product_id': line.product_id.id,
                                                                 'price_unit': price_unit_for_ewallet_line,
                                                                 'tax_ids': [(4, tax_id) for tax_id in line.tax_id.ids],
                                                                 'is_reward_line': True,
                                                                 'reward_id': line.reward_id.id})
                                                         )
                                else:
                                    line_to_unlink = invoice.invoice_line_ids.filtered(
                                        lambda
                                            x: x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.reward_id.id == line.reward_id.id)
                                    if line_to_unlink:
                                        line_to_unlink.unlink()

                        if value:
                            invoice.write({'invoice_line_ids': value})


                else:
                    order_id = invoice.invoice_line_ids.sale_line_ids.order_id
                    having_discount_lines = order_id.order_line.filtered(
                        lambda
                            x: x.is_reward_line and x.reward_id.program_id.need_to_exclude_from_automatic_sign and x.reward_id.program_id.program_type == 'promotion')
                    if order_id and having_discount_lines:
                        values = []
                        for line in having_discount_lines:
                            discount = line.reward_id.discount
                            discountable = 0
                            invoice_line_ids = invoice.invoice_line_ids.filtered(
                                lambda
                                    x: not x.is_reward_line and x.tax_ids.ids == line.tax_id.ids and x.product_type == "consu" and x.product_id.is_storable)
                            if invoice_line_ids:
                                for invoice_line in invoice_line_ids:
                                    discountable += invoice_line.price_unit * invoice_line.quantity * (
                                            1 - (invoice_line.discount or 0.0) / 100.0)

                                unit_price_of_reward_line = round((round(discountable, 2) * discount) / 100, 2)
                                values.append((0, 0, {'product_id': line.product_id.id,
                                                      'price_unit': -(unit_price_of_reward_line),
                                                      'tax_ids': [(4, tax_id) for tax_id in line.tax_id.ids],
                                                      'is_reward_line': True,
                                                      'reward_id': line.reward_id.id
                                                      })
                                              )
                        invoice.write({'invoice_line_ids': values})
                    if invoice.move_type == 'out_invoice':
                        having_ewallet_lines = order_id.order_line.filtered(
                            lambda x: x.is_reward_line and x.reward_id.program_id.program_type == 'ewallet')
                        if order_id and having_ewallet_lines:
                            values = []
                            for line in having_ewallet_lines:
                                delivery_line_id = sale_order_id.order_line.filtered(
                                    lambda x: x.is_delivery and x.tax_id.ids == line.tax_id.ids)
                                invoiced_delivery_line_id = invoice.invoice_line_ids.filtered(lambda
                                                                                                  x: x.product_id == delivery_line_id.product_id and x.tax_ids.ids == delivery_line_id.tax_id.ids)
                                invoice_line_ids = invoice.invoice_line_ids.filtered(
                                    lambda
                                        x: x.tax_ids.ids == line.tax_id.ids and not x.reward_id.program_id.program_type == "ewallet")
                                if invoiced_delivery_line_id and invoice_line_ids:
                                    if invoiced_delivery_line_id.id not in invoice_line_ids.ids:
                                        invoice_line_ids += invoiced_delivery_line_id
                                else:
                                    if invoiced_delivery_line_id:
                                        invoice_line_ids = invoiced_delivery_line_id
                                sale_order_line_product_same_taxes_ids = sale_order_id.order_line.filtered(
                                    lambda
                                        x: x.tax_id.ids == line.tax_id.ids and not x.reward_id.program_id.program_type == "ewallet")
                                if invoice_line_ids and sale_order_line_product_same_taxes_ids:
                                    invoice_lines_price_total = sum(invoice_line_ids.mapped('price_total'))
                                    sale_order_lines_price_total = sum(
                                        sale_order_line_product_same_taxes_ids.mapped('price_total'))
                                    if invoice_lines_price_total and sale_order_lines_price_total:
                                        price_total_for_ewallet_line = (
                                                                               invoice_lines_price_total * line.price_total) / sale_order_lines_price_total
                                        tax_amount_total = 0
                                        for tax_id in line.tax_id:
                                            if tax_id.children_tax_ids:
                                                for children_tax_id in tax_id.children_tax_ids:
                                                    if (
                                                            not children_tax_id.price_include or children_tax_id.include_base_amount):
                                                        tax_amount_total += children_tax_id.amount
                                                continue
                                            if (not tax_id.price_include or tax_id.include_base_amount):
                                                tax_amount_total += tax_id.amount
                                        price_unit_for_ewallet_line = (
                                                (price_total_for_ewallet_line * 100) / (100 + tax_amount_total))
                                        if (taxes_ids := [tax for tax in line.tax_id if tax.include_base_amount]
                                                         or [child_tax for child_tax in line.tax_id.children_tax_ids if
                                                             child_tax.include_base_amount]):
                                            total_void_amount = 0
                                            for taxes_id in taxes_ids:
                                                if taxes_id.price_include:
                                                    total_void_amount += taxes_id.amount
                                                else:
                                                    continue
                                            price_unit_for_ewallet_line = (
                                                (price_unit_for_ewallet_line * (1.0 + total_void_amount / 100.0)))
                                        values.append((0, 0, {'product_id': line.product_id.id,
                                                              'price_unit': price_unit_for_ewallet_line,
                                                              'tax_ids': [(4, tax_id) for tax_id in line.tax_id.ids],
                                                              'is_reward_line': True,
                                                              'reward_id': line.reward_id.id})
                                                      )
                            invoice.write({'invoice_line_ids': values})
        return res
