# -*- coding: utf-8 -*-
from datetime import timedelta
import logging

_logger = logging.getLogger("picking_isuues")
from odoo import fields, models,api,_
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warehouses_stock = fields.Text(
        store=False, readonly=True,
    )

    @api.model
    def get_warehouses_stock(self, line_id):
        """
            Authour: nidhi@setconsulting
            Date: 6/12/2024
            Task: Migration from V16 to V18
            Purpose: This method is used to get stock of products present in the warehouse and if the sale order line is
                     not saved than it will give error.
        """
        line_id = self.browse(line_id)
        if not line_id:
            raise UserError(_('To view Stock By Warehouse Table kindly save the Sale Order'))
        return line_id.product_id.with_context(warehouse_id=line_id.warehouse_id.id)._compute_get_quantity_warehouses_dict()

    def _prepare_procurement_values_by_warehouse(self, group_id=False, warehouse_id=False):
        """
            Authour: nidhi@setconsulting
            Date: 6/12/2024
            Task: Migration from V16 to V18
            Purpose: This method is called from method: _action_launch_stock_rule_by_warehouse. The group_id will be mentioned
                    from the method : _action_launch_stock_rule_by_warehouse. This method will update values of sale_order_line and
                    if there is commitment_date(Delivery Date) in sale_order then it will update date_planned
            Return : values
        """
        values = self._prepare_procurement_values(group_id=group_id)
        self.ensure_one()
        date_planned = self.order_id.date_order \
                       + timedelta(days=self.customer_lead or 0.0) - timedelta(
            days=self.order_id.company_id.security_lead)
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': warehouse_id,
            'partner_id': self.order_id.partner_shipping_id.id,
        })
        for line in self.filtered("order_id.commitment_date"):
            date_planned = fields.Datetime.from_string(line.order_id.commitment_date) - timedelta(
                days=line.order_id.company_id.security_lead)
            values.update({
                'date_planned': fields.Datetime.to_string(date_planned),
            })
        return values

    def _get_warehouse_to_picking(self):
        """
            Authour: nidhi@setconsulting
            Date: 6/12/2024
            Task: Migration from V16 to V18
            Purpose : This method is called from def _action_launch_stock_rule.This method is used to count quantity as well as add
                      first_picking in res.
                      The development of  len(bom_id) will work when the bom is created of the same product which is present in sale_order_line.
            Return : is_phantom, res_list
        """
        res = res_list = []
        warehouse = self.env['stock.warehouse']
        is_phantom = False
        is_mrp_installed = self.env['ir.module.module'].sudo().search(
            [('name', '=', 'mrp')], limit=1)

        for line in self.filtered(
                lambda line: (line.state == 'sale' or line.product_id.type in ('consu')) and line.product_id):
            qty_added = 0
            first_picking = {}
            generate_picking_flag = False
            product_tmpl_id = line.product_id.product_tmpl_id.sudo()

            if is_mrp_installed.state == 'installed':
                bom_id = product_tmpl_id.bom_ids.filtered(lambda bom: bom.type == 'phantom')

            else:
                bom_id = []

            if len(bom_id) > 0:
                is_phantom = True

                for bom_line in bom_id.bom_line_ids:
                    qty_available_by_wh = bom_line.product_id.with_context(
                        warehouse_id=line.warehouse_id.id, order_id=line.order_id.id
                    )._compute_get_quantity_warehouses_dict()

                    qty_picking = bom_line.product_qty * line.product_uom_qty

                    for wh in qty_available_by_wh['content']:
                        reserved = 0
                        saleable = wh['free_qty']
                        pick = list(filter(lambda p: (
                                p['product_id'] == bom_line.product_id.id and p[
                            'warehouse_id'].id == wh['warehouse_id']), res))

                        if len(pick) > 0:
                            for p in pick:
                                reserved += p['qty']

                        if qty_picking < 0:
                            break

                        if saleable <= 0.0:
                            generate_picking_flag = True
                            continue

                        saleable = saleable - reserved

                        if wh['warehouse_id'] == line.warehouse_id.id:
                            if saleable > qty_picking:
                                first_picking = {'warehouse_id': line.warehouse_id,
                                                 'qty': qty_picking,
                                                 'product_id': bom_line.product_id.id, 'line': line}
                                res.append(first_picking)
                                qty_picking = 0
                                break
                            elif saleable <= qty_picking:
                                first_picking = {'warehouse_id': line.warehouse_id, 'qty': saleable,
                                                 'product_id': bom_line.product_id.id, 'line': line}
                                qty_picking = qty_picking - saleable

                            res.append(first_picking)
                            qty_added += 1
                        else:
                            warehouse_obj = warehouse.sudo().search(
                                [('id', '=', wh['warehouse_id'])])

                            # if (wh['saleable'] - qty_picking) <= 0.0:
                            if saleable > qty_picking:
                                res.append({'warehouse_id': warehouse_obj, 'qty': qty_picking,
                                            'product_id': bom_line.product_id.id, 'line': line})
                                qty_picking = qty_picking - saleable
                                qty_added += 1
                            elif saleable <= qty_picking:
                                res.append({'warehouse_id': warehouse_obj, 'qty': saleable,
                                            'product_id': bom_line.product_id.id, 'line': line})
                                qty_picking = qty_picking - saleable
                                qty_added += 1

                    if qty_added == 0 and not generate_picking_flag:
                        first_picking = {'warehouse_id': line.warehouse_id,
                                         'qty': line.product_uom_qty * bom_line.product_qty,
                                         'product_id': bom_line.product_id.id, 'line': line}
                        res.append(first_picking)
                        qty_picking = 0
                    elif qty_picking > 0 and len(first_picking) > 0:
                        first_picking['qty'] = first_picking['qty'] + qty_picking
                    # if not self.env['ir.config_parameter'].sudo().get_param(
                    # 		'demand_fullfill_by_highest_fillfiller_wh.optimized_warehouse'):
                    if qty_picking > 0 and len(first_picking) == 0:
                        wh_obj = warehouse.sudo().browse(
                            qty_available_by_wh['content'][0]['warehouse_id'])
                        first_picking = {'warehouse_id': wh_obj, 'qty': qty_picking,
                                         'product_id': bom_line.product_id.id, 'line': line}
                        res.append(first_picking)
                        qty_picking = 0
            else:
                qty_available_by_wh = line.product_id.with_context(
                    warehouse_id=line.warehouse_id.id, qty_picking=line.product_uom_qty,
                    order_id=line.order_id.id
                )._compute_get_quantity_warehouses_dict()

                qty_picking = line.product_uom_qty

                for wh in qty_available_by_wh['content']:
                    reserved = 0
                    saleable = wh['free_qty']
                    pick = list(filter(lambda p: (
                            p['product_id'] == line.product_id.id and p['warehouse_id'].id ==
                            wh['warehouse_id']), res))

                    if len(pick) > 0:
                        for p in pick:
                            reserved += p['qty']

                    if qty_picking < 0:
                        break

                    if saleable <= 0.0:
                        generate_picking_flag = True
                        continue

                    saleable = saleable - reserved

                    if wh['warehouse_id'] == line.warehouse_id.id:
                        if saleable > qty_picking:
                            first_picking = {'warehouse_id': line.warehouse_id, 'qty': qty_picking,
                                             'product_id': line.product_id.id, 'line': line}
                            res.append(first_picking)
                            qty_picking = 0
                            generate_picking_flag = True
                            break
                        elif saleable <= qty_picking:
                            first_picking = {'warehouse_id': line.warehouse_id, 'qty': saleable,
                                             'product_id': line.product_id.id, 'line': line}
                            qty_picking = qty_picking - saleable

                        res.append(first_picking)
                        generate_picking_flag = True
                        qty_added += 1
                    else:
                        warehouse_obj = warehouse.sudo().browse(wh['warehouse_id'])
                        # if (wh['saleable'] - qty_picking) <= 0.0:
                        if saleable > qty_picking:
                            res.append({'warehouse_id': warehouse_obj, 'qty': qty_picking,
                                        'product_id': line.product_id.id, 'line': line})
                            qty_picking = qty_picking - saleable
                            qty_added += 1
                            generate_picking_flag = True
                        elif saleable <= qty_picking:
                            res.append({'warehouse_id': warehouse_obj, 'qty': saleable,
                                        'product_id': line.product_id.id, 'line': line})
                            qty_picking = qty_picking - saleable
                            qty_added += 1
                            generate_picking_flag = True

                if qty_added == 0 and not generate_picking_flag:
                    first_picking = {'warehouse_id': line.warehouse_id, 'qty': line.product_uom_qty,
                                     'product_id': line.product_id.id, 'line': line}
                    res.append(first_picking)
                    qty_picking = 0
                elif qty_picking > 0 and len(first_picking) > 0:
                    first_picking['qty'] = first_picking['qty'] + qty_picking
                # if not self.env['ir.config_parameter'].sudo().get_param(
                # 		'demand_fullfill_by_highest_fillfiller_wh.optimized_warehouse'):
                if qty_picking > 0 and len(first_picking) == 0:
                    wh_obj = warehouse.sudo().browse(
                        qty_available_by_wh['content'][0]['warehouse_id'])
                    first_picking = {'warehouse_id': wh_obj, 'qty': qty_picking,
                                     'product_id': line.product_id.id, 'line': line}
                    res.append(first_picking)
                    qty_picking = 0

        res = list(filter(lambda r: r['qty'] > 0, res))
        res_list = [i for n, i in enumerate(res) if i not in res[n + 1:]]
        _logger.info(f"selected_picking_lines ==>{res_list}")
        return is_phantom, res_list

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Authour: nidhi@setconsulting
        Date: 6/12/2024
        Task: Migration from V16 to V18
        Purpose:Launch procurement group run method with required/custom fields genrated by a
                sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
                depending on the sale order line product rule.
        """
        if self:  # this part is to not create transfers for imported FBA orders in manuall they are allowed to create Pickings
            ama_channel = self.order_id.amazon_channel
            if ama_channel == 'fba' and not self.order_id.is_amazon_order_manually:
                return True
        result = True
        is_phantom, res = self._get_warehouse_to_picking()

        if len(res) > 0:
            if is_phantom:
                result = self._action_launch_stock_rule_by_warehouse(res, is_phantom)
            else:
                result = self._action_launch_stock_rule_by_warehouse(res)

            orders = list(set(x.order_id for x in self))
            for order in orders:
                reassign = order.picking_ids.filtered(lambda x: x.state == 'confirmed' or (
                        x.state in ['waiting', 'assigned'] and not x.printed))
                if reassign:
                    reassign.action_assign()
            return result

        res = super(SaleOrderLine, self)._action_launch_stock_rule()
        return res

    def _action_launch_stock_rule_by_warehouse(self, pickings, is_phantom=False):
        """
            Authour: nidhi@setconsulting
            Date: 6/12/2024
            Task: Migration from V16 to V18
            Purpose: This method is called from the method : _action_launch_stock_rule.
                     Primarily, this method is used to create procurement_group_id if line.order_id has no procurement_group_id.
                    Group Id will be passes to the method : _prepare_procurement_values_by_warehouse.
                    This method will create a record in Procurement.group and may pass error if it occurs.
            Return : True
        """
        errors = []

        for pick in pickings:
            line = pick['line']
            product_uom_qty = pick['qty']
            warehouse_id = pick['warehouse_id']
            qty = 0
            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values_by_warehouse(group_id=group_id,
                                                                   warehouse_id=warehouse_id)

            product_qty = product_uom_qty - qty
            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom,
                                                                 rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                if is_phantom:
                    product_id = self.env['product.product'].sudo().search(
                        [('id', '=', pick['product_id'])])
                else:
                    product_id = line.product_id.filtered(lambda x:x.type == "consu" or x.is_storable)
                    if not product_id:
                        continue
                self.env['procurement.group'].run([self.env['procurement.group'].Procurement(
                    product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, self.env.user.company_id,
                    values
                )])
            except UserError as error:
                  errors.append(str(error))
        if errors:
            raise UserError('\n'.join(errors))

        return True