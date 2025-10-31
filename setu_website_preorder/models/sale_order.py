from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

stocktype = ''
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.is_preorder')
    def _get_preorder_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the field Pre-Order from the line.
        """
        for order in self:
            if any(line.is_preorder for line in order.order_line):
                order.is_preorder = True
            else:
                order.is_preorder = False

    @api.depends('order_line.is_presale')
    def _get_presale_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the field Pre-Sale from the line.
        """
        for order in self:
            if any(line.is_presale for line in order.order_line):
                order.is_presale = True

            else:
                order.is_presale = False

    @api.depends('order_line.is_international_preorder')
    def _get_international_preorder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the field International Preorder from the line.
        """
        for order in self:
            if any(line.is_international_preorder for line in order.order_line):
                order.is_international_preorder = True

            else:
                order.is_international_preorder = False

    @api.depends('order_line.is_exclusive')
    def _get_exclusive_international_preorder(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the field Exclusive International Preorder from the line.
        """
        for order in self:
            if any(line.is_exclusive for line in order.order_line):
                order.is_exclusive_international_preorder = True

            else:
                order.is_exclusive_international_preorder = False

    @api.depends('order_line.is_next_day_shipping')
    def _get_next_day_shipping_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the field Next Day Shipping from the line.
        """
        for order in self:
            if any(line.is_next_day_shipping for line in order.order_line):
                order.is_next_day_shipping = True
            else:
                order.is_next_day_shipping = False

    is_preorder = fields.Boolean(string="Pre-Order",
                                 compute=_get_preorder_order,
                                 store=True, readonly=True,
                                 default=False, copy=False)

    is_presale = fields.Boolean(string="Pre-Sale",
                                compute=_get_presale_order,
                                store=True, readonly=True,
                                default=False, copy=False)
    is_international_preorder = fields.Boolean(string="International Preorder",
                                                compute=_get_international_preorder,
                                                store=True, readonly=True,
                                                default=False, copy=False)
    is_exclusive_international_preorder = fields.Boolean(string="Exclusive International Preorder",
                                               compute=_get_exclusive_international_preorder,
                                               store=True, readonly=True,
                                               default=False, copy=False)

    is_next_day_shipping = fields.Boolean(string="Next Day Shipping",
                                 compute=_get_next_day_shipping_order,
                                 store=True, readonly=True,
                                 default=False, copy=False)

    cancel_order_time_limit = fields.Datetime(string="Time limit to cancel order", help="Time limit upto which customer can cancel the order", copy=False)
    sale_order_cancel_from_website = fields.Boolean(string="Order cancelled from Website",default=False,copy=False)



    def set_temp_stock_type(self, stock_type):
        global stocktype
        stocktype = stock_type

    def _get_cart_and_free_qty(self, product, line=None):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose: Override the method to cart and product qty conditionality(presale, preorder, international preorder, instock)
        """
        self.ensure_one()
        if not line and not product:
            return 0, 0
        if not product:
            product = line.product_id

        cart_qty = sum(self._get_common_product_lines(line, product).mapped('product_uom_qty'))
        # stock_type = self.env.context.get('stock_type')
        if product.available_for_presale and (stocktype == 'presale' or
                self.is_presale):
            return cart_qty, product.presale_qty
        elif product.available_for_preorder and (stocktype == 'preorder' or
                self.is_preorder):
            return cart_qty, product.preorder_qty
        elif product.is_international_pre_order_product and (stocktype == 'international_preorder' or
                                                             self.is_international_preorder):
            return cart_qty,product.international_preorder_qty
        else:
            website = self.env['website'].get_current_website()
            conf_warehouses = website._get_website_location_type()
            free_qty = product.with_context(warehouse_id=conf_warehouses).free_qty
            return cart_qty, free_qty

    def _prepare_order_line_update_values(
            self, order_line, quantity, linked_line_id=False, **kwargs):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the boolean as per the order(preorder, presale, international preorder, next day shipping)
        """
        vals = super()._prepare_order_line_update_values(
            order_line, quantity, linked_line_id, **kwargs)
        if kwargs.get('stock_type') == 'preorder' or self.is_preorder:
            vals['is_preorder'] = True
        if kwargs.get('stock_type') == 'presale' or self.is_presale:
            vals['is_presale'] = True
        if kwargs.get('stock_type') == 'international_preorder' or self.is_international_preorder:
            vals['is_international_preorder'] = True
        if kwargs.get('stock_type') == 'international_preorder' and (order_line.is_exclusive or kwargs.get('is_exclusive')):
            vals['is_international_preorder'] = True
            vals['is_exclusive'] = True
        if self.is_next_day_shipping or kwargs.get('stock_type') == 'is_next_day_shipping':
            vals['is_next_day_shipping'] = True
        return vals

    def _prepare_order_line_values(
            self, product_id, quantity, linked_line_id=False,
            no_variant_attribute_value_ids=None, product_custom_attribute_values=None,
            combo_item_id=None,
            **kwargs
    ):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the boolean as per the order(preorder, presale, international preorder, next day shipping).
        """
        vals = super()._prepare_order_line_values(product_id, quantity, linked_line_id,
                                                  no_variant_attribute_value_ids,
                                                  product_custom_attribute_values, combo_item_id, **kwargs)
        if kwargs.get('stock_type') == 'preorder':
            vals['is_preorder'] = True
        if kwargs.get('stock_type') == 'presale':
            vals['is_presale'] = True
        if kwargs.get('stock_type') == 'international_preorder':
            vals['is_international_preorder'] = True
        if kwargs.get('stock_type') == 'international_preorder' and kwargs.get('is_exclusive') == 'True':
            vals['is_exclusive'] = True
        if kwargs.get('stock_type') == 'is_next_day_shipping':
            vals['is_next_day_shipping'] = True
        return vals

    def action_confirm(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set the cancel order limit only for normal orders and called _link_to_po for connect the relation
            between so and po for presale and preorder and from this different operation are perform here also national
            preorder notification related part are included.
        """

        is_linked = self._link_to_po()
        if not (self.is_presale or self.is_preorder or self.is_international_preorder or self.is_next_day_shipping):
            website_id = self.env["website"].get_current_website()
            if website_id.enable_cancellation_sale_order:
                self.cancel_order_time_limit = self.date_order + timedelta(hours=self.env["website"].get_current_website().time_limit_to_cancel_order)
                self.message_post(
                    body=_("Time limit to cancel order %s") % (self.cancel_order_time_limit)
                )
        if is_linked:
            if self.is_exclusive_international_preorder:
                exclusive_international_preorder_product = self.order_line.filtered(
                lambda x: x.product_id.is_storable and x.is_exclusive)
                for exclusive_line in exclusive_international_preorder_product:
                    if not exclusive_line.product_id.exclusive_partner_id:
                        exclusive_line.product_id.exclusive_partner_id = self.partner_id
                        self.message_post(
                            body=_(
                                "Exclusive Partner is set for this product %s") % (
                                     exclusive_line.product_id.name)
                        )
                    elif exclusive_line.product_id.exclusive_partner_id == self.partner_id:
                        self.message_post(
                            body=_(
                                "Exclusive Partner is already set for this product %s") % (exclusive_line.product_id.name)
                        )
                    else:
                        raise UserError(_("Product %s is already available for other customer",exclusive_line.product_id.name))
            res = super().action_confirm()
            sale_purchase_rel = self.env['preorder.sale.purchase.rel'].search([('sale_id', '=', self.id)])
            user_ids = self.env['website'].sudo().get_current_website().activity_owner_ids.ids
            config_quantity = self.env['website'].sudo().get_current_website().config_quantity
            if config_quantity > 0.0 and user_ids:
                for order in sale_purchase_rel.purchase_id:
                    order_name = order.name
                    total_quantity_of_current_po = order.order_line.mapped('pre_ordered_qty')
                    sum_of_quantities_of_current_po = sum(total_quantity_of_current_po)
                    if sum_of_quantities_of_current_po >= config_quantity:
                        note = f'Config Quantity are {config_quantity} and the order {order_name} are exceeds this config quantity.'
                        for user_id in user_ids:
                            activity = self.env['mail.activity'].create({
                                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                                'res_id': order.id,
                                'res_model_id': self.env.ref('purchase.model_purchase_order').id,
                                'user_id': user_id,
                                'note': note
                            })
                            activity.action_close_dialog()
            return res
        else:
            if self.is_exclusive_international_preorder:
                exclusive_international_preorder_product = self.order_line.filtered(
                    lambda x: x.product_id.is_storable and x.is_exclusive)
                for exclusive_line in exclusive_international_preorder_product:
                    if exclusive_line.product_id.exclusive_partner_id:
                        raise UserError(
                            _("Product %s is already available for other customer", exclusive_line.product_id.name))
                    else:
                        raise UserError(_("This order can't be confirmed because the [%s] %s is already exclusive to another customer.", exclusive_line.product_id.default_code,exclusive_line.product_id.name))
            else:
                raise UserError(_("The Pre-Sale order contains products that have already been received (in stock). In order to confirm the order, delete the products in stock. "))

    def action_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: unlink and remove the connection with the model which are connect the po and so also removed the
            value of the Time limit to cancel order during the cancel order.
        """
        for rec in self:
            if rec.is_presale:
                self.env['presale.purchase.rel'].search([('sale_id', '=', rec.id)]).unlink()
            elif rec.is_preorder:
                self.env['preorder.sale.purchase.rel'].search([('sale_id', '=', rec.id)]).unlink()
            elif rec.is_international_preorder:
                self.env['international.preorder.sale.purchase.rel'].search([('sale_id','=',rec.id)]).unlink()
            if rec.cancel_order_time_limit:
                rec.message_post(
                    body=_("Order is cancel on: %s") % ( datetime.now())
                )
                rec.cancel_order_time_limit = False
        return super().action_cancel()

    def _link_to_po(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: called during the confirm the order and connect relation between the po and so via the creating a records of model preorder.sale.purchase.rel, presale.purchase.rel, international.preorder.sale.purchase.rel   
        """
        for rec in self:
            preorder_products = rec.order_line.filtered(
                lambda x: x.product_id.is_storable and x.is_preorder)
            presale_products = rec.order_line.filtered(
                lambda x: x.product_id.is_storable and x.is_presale)
            international_preorder_product = rec.order_line.filtered(
                lambda x: x.product_id.is_storable and x.is_international_preorder)
            so_po_rel_obj = self.env['preorder.sale.purchase.rel'].sudo()

            for record in preorder_products:
                purchase_lines = record.product_id.preorder_presale_po_search(
                    'available_for_preorder')
                total_required = record.product_uom_qty

                if purchase_lines:
                    for pl in purchase_lines:
                        if total_required > 0:
                            total_pre_available = pl.product_uom_qty - pl.pre_ordered_qty
                            if total_required <= total_pre_available:
                                pre_ordered_qty = (total_required)
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'preorder_qty': pre_ordered_qty}
                                so_po_rel_obj.create(rel_dict)
                                total_required -= total_required
                            elif total_required > total_pre_available:
                                total_required -= total_pre_available
                                pre_ordered_qty = total_pre_available
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'preorder_qty': pre_ordered_qty}
                                so_po_rel_obj.create(rel_dict)
                else:
                    return False
            so_po_rel_obj = self.env['presale.purchase.rel'].sudo()
            for record in presale_products:
                purchase_lines = record.product_id.preorder_presale_po_search(
                    'available_for_presale')
                total_required = record.product_uom_qty
                if purchase_lines:
                    for pl in purchase_lines:
                        if total_required > 0:
                            total_pre_available = pl.product_uom_qty - pl.pre_sale_qty
                            if total_required <= total_pre_available:
                                pre_sale_qty = (total_required)
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'presale_qty': pre_sale_qty}
                                so_po_rel_obj.create(rel_dict)
                                total_required -= total_required
                                if record.tentative_arrival_date:
                                    record.tentative_arrival_date += ',' + str(pl.order_id.date_planned.date())
                                else:
                                    record.tentative_arrival_date = str(pl.order_id.date_planned.date())
                            elif total_required > total_pre_available:
                                total_required -= total_pre_available
                                pre_sale_qty = total_pre_available
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'presale_qty': pre_sale_qty}
                                so_po_rel_obj.create(rel_dict)
                                if record.tentative_arrival_date:
                                    record.tentative_arrival_date += ',' + str(pl.order_id.date_planned.date())
                                else:
                                    record.tentative_arrival_date = str(pl.order_id.date_planned.date())
                else:
                    return False
            so_po_rel_obj = self.env['international.preorder.sale.purchase.rel'].sudo()
            for record in international_preorder_product:
                purchase_lines = record.product_id.preorder_presale_po_search(
                    'is_international_pre_order_product')
                total_required = record.product_uom_qty

                if purchase_lines:
                    for pl in purchase_lines:
                        if total_required > 0:
                            total_pre_available = pl.product_uom_qty - pl.international_pre_order_qty
                            if total_required <= total_pre_available:
                                pre_ordered_qty = (total_required)
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'international_preorder_qty': pre_ordered_qty}
                                so_po_rel_obj.create(rel_dict)
                                total_required -= total_required
                            elif total_required > total_pre_available:
                                total_required -= total_pre_available
                                pre_ordered_qty = total_pre_available
                                rel_dict = {'purchase_id': pl.order_id.id, 'sale_id': rec.id,
                                            'sale_line_id': record.id, 'purchase_line_id': pl.id,
                                            'international_preorder_qty': pre_ordered_qty}
                                so_po_rel_obj.create(rel_dict)
                else:
                    return False
        return True

    def _prepare_invoice(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose: set is_next_day_shipping in picking invoice.
        """
        vals = super(SaleOrder, self)._prepare_invoice()
        vals.update({'is_next_day_shipping': self.is_next_day_shipping})
        return vals

    def _get_delivery_methods(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 15/04/25
            Task: Migration to v18 from v16
            Purpose: To set only those Shipping Methods on the Website in which NEXT DAY SHIPPING is set otherwise it will not show any other
                     shipping method even though they are published only for next day shipping sale order.
        """
        res = super(SaleOrder, self)._get_delivery_methods()
        if self.is_next_day_shipping:
            return self.env['delivery.carrier'].sudo().search([
                ('website_published', '=', True),('is_next_day_shipping','=',True)
            ]).filtered(lambda carrier: carrier._is_available_for_order(self))
        if not self.is_next_day_shipping:
            return self.env['delivery.carrier'].sudo().search([
                ('website_published', '=', True), ('is_next_day_shipping', '=', False)
            ]).filtered(lambda carrier: carrier._is_available_for_order(self))
        return res

    def _is_reorder_allowed(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16 --> Website - enhancement { https://app.clickup.com/t/86dtwa8bt }
            Purpose: As per the condition : The button should appear on ALL orders that are in status (cancel and sale order).
        """
        res = super(SaleOrder, self)._is_reorder_allowed()
        if self.state in ('sale','cancel'):
            return any(line._is_reorder_allowed() for line in self.order_line if not line.display_type)
        return res