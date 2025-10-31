from odoo import models, api, fields, registry, SUPERUSER_ID, _
from odoo.exceptions import UserError
from markupsafe import Markup

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_preorder_type = fields.Boolean(string="Available for Pre-order",
                                      help="Enabled the field to display the "
                                           "product as pre-order once it is below "
                                           "the specified minimum quantity.",
                                      default=False,
                                      copy=False)
    preorder_rel_ids = fields.One2many("preorder.sale.purchase.rel", 'purchase_id',
                                       string="Pre-order Details",
                                       copy=False,
                                       domain=[('preorder_qty', '>', 0), ('pre_order_state', 'in', ['sale'])])
    fulfill_percentage = fields.Float(string="Order Fulfilled",
                                      compute="_calculate_po_fulfill_percentage",
                                      store=False,
                                      copy=False)

    is_presale_type = fields.Boolean(string="Available for Pre-Sale",
                                     help="Enabled the field to display the "
                                          "product as pre-Sale once it is below "
                                          "the specified minimum quantity.",
                                     default=False,
                                     copy=False)
    presale_rel_ids = fields.One2many("presale.purchase.rel", 'purchase_id',
                                      string="Pre-Sale Details",
                                      copy=False,
                                      domain=[('presale_qty', '>', 0), ('pre_sale_state', 'in', ['sale'])])
    presale_fulfill_percentage = fields.Float(string="Order Fulfilled",
                                              compute="_calculate_presale_fulfill_percentage",
                                              store=False,
                                              copy=False)
    is_international_pre_order = fields.Boolean(string="Is International pre-order",default=False,copy=False)
    international_preorder_rel_ids = fields.One2many("international.preorder.sale.purchase.rel",'purchase_id',
                                                     string="International Pre-order Details",
                                                     copy=False,
                                                     domain=[('international_preorder_qty','>',0),('international_pre_order_state','in',['sale'])])
    international_fulfill_percentage = fields.Float(string="International Order Fulfilled",
                                      compute="_calculate_international_po_fulfill_percentage",
                                      store=False,
                                      copy=False)


    def _calculate_po_fulfill_percentage(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: calculate the Order Fulfilled for preorder to know how much percent order are fulfilled.
        """
        self.fulfill_percentage = 0
        for record in self.filtered(lambda x: x.is_preorder_type):
            order_lines = record.order_line.filtered(lambda x: x.product_id.is_storable)
            if order_lines:
                line_wise_percentage = sum([(rec.pre_ordered_qty * 100) / rec.product_qty
                                            if rec.product_qty > 0 and rec.pre_ordered_qty > 0 else 0
                                            for rec in order_lines]) or 0
                record.fulfill_percentage = line_wise_percentage / len(order_lines)


    def _calculate_presale_fulfill_percentage(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: calculate the Order Fulfilled for presale to know how much percent order are fulfilled.
        """
        self.presale_fulfill_percentage = 0
        for record in self.filtered(lambda x: x.is_presale_type):
            order_lines = record.order_line.filtered(lambda x: x.product_id.is_storable)
            if order_lines:
                line_wise_percentage = sum([(rec.pre_sale_qty * 100) / rec.product_qty
                                            if rec.product_qty > 0 and rec.pre_sale_qty > 0 else 0
                                            for rec in order_lines]) or 0
                record.presale_fulfill_percentage = line_wise_percentage / len(order_lines)


    def _calculate_international_po_fulfill_percentage(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: calculate the Order Fulfilled for international preorder to know how much percent order are fulfilled.
        """
        self.international_fulfill_percentage = 0
        for record in self.filtered(lambda x: x.is_international_pre_order):
            order_lines = record.order_line.filtered(lambda x: x.product_id.is_storable)
            if order_lines:
                line_wise_percentage = sum([(rec.international_pre_order_qty * 100) / rec.product_qty
                                            if rec.product_qty > 0 and rec.international_pre_order_qty > 0 else 0
                                            for rec in order_lines]) or 0
                record.international_fulfill_percentage = line_wise_percentage / len(order_lines)

    def button_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 16/04/25
            Task: Migration to v18 from v16
            Purpose: during cancel the po checked po status and recalculate the presale, preorder quantity of products.
        """
        self.check_preorder_po_cancel_status()
        res = super(PurchaseOrder, self).button_cancel()
        self.order_line.product_id._compute_available_for_presale()
        self.order_line.product_id._compute_available_for_preorder()
        return res

    def check_preorder_po_cancel_status(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 16/04/25
            Task: Migration to v18 from v16
            Purpose: checked if the po is not linked to the so then cancel normally else not cancelled and raise warning as per the condition.
        """
        for record in self:
            if not record.is_preorder_type and not record.is_presale_type and not record.is_international_pre_order:
                continue
            so_rel_ids = record.mapped('preorder_rel_ids').filtered(
                lambda x: x.pre_order_state != 'cancel')
            current_order_lines = so_rel_ids and so_rel_ids.filtered(lambda x: x.preorder_qty > 0) or False

            so_prerel_ids = record.mapped('presale_rel_ids').filtered(
                lambda x: x.pre_sale_state != 'cancel')
            current_presale_lines = so_prerel_ids and so_prerel_ids.filtered(lambda x: x.presale_qty > 0) or False

            int_so_prerel_ids = record.mapped('international_preorder_rel_ids').filtered(
                lambda x: x.international_pre_order_state != 'cancel')
            current_int_preorder_lines = int_so_prerel_ids and int_so_prerel_ids.filtered(lambda x: x.international_preorder_qty > 0) or False

            if current_order_lines and not record._context.get('convert_to_presale'):
                current_order_lines_str = "\n".join(map(str, current_order_lines.mapped('sale_id').mapped('name')))
                raise UserError("You can't cancel/delete this order/line as some of the products of this Purchase Order "
                              "is already pre-ordered in few Sale Orders,\n%s" % current_order_lines_str)

            if current_presale_lines:
                current_order_lines_str1 = "\n".join(map(str, current_presale_lines.mapped('sale_id').mapped('name')))
                raise UserError("You can't cancel/delete this order/line as some of the products of this Purchase Order "
                              "is already pre-sale in few Sale Orders,\n%s" % current_order_lines_str1)

            if current_int_preorder_lines:
                int_current_order_lines_str = "\n".join(map(str, current_int_preorder_lines.mapped('sale_id').mapped('name')))
                raise UserError("You can't cancel/delete this order/line as some of the products of this Purchase Order "
                              "is already pre-ordered in few Sale Orders,\n%s" % int_current_order_lines_str)


    def button_confirm(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/04/25
            Task: Migration to v18 from v16
            Purpose: Added action = self.env.context.get('po_force_confirm') in flow of button_confirm as per the wizard (purchase_order_confirm_wizard.py)
        """
        action = self.env.context.get('po_force_confirm')
        if action or self._context.get('convert_to_presale'):
            for order in self:
                if not order.is_preorder_type:
                    continue
                total_lines = order.order_line
                order_lines = total_lines.filtered(lambda x: x.product_uom_qty < x.pre_ordered_qty)
                if order_lines:
                    raise UserError("You can not confirm less quantities then the pre-ordered quantities for the following "
                                  "products,\n%s" % (" ,".join(order_lines.mapped('product_id.name'))))
            result = super(PurchaseOrder, self).button_confirm()
            return result
        else :
            return {
                'name': 'CONFIRMATION',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'purchase.order.confirm.wizard',
            }
    # This method is used for convert pre-order to pre-sale while click the (convert to pre-sale) button
    def convert_presale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 28/04/25
            Task: Migration to v18 from v16
            Purpose: convert the order from preorder to presale.
        """
        self.ensure_one()
        new_po = self.copy()
        if self.is_preorder_type:
            for order in self.order_line:
                if order.pre_ordered_qty:
                    order.product_qty = order.pre_ordered_qty
                else:
                    order.unlink()

            for product in self.order_line.mapped('product_id'):
                preorder_line_ids = self.order_line.filtered(lambda l: l.product_id == product)
                presale_line_ids = new_po.order_line.filtered(lambda l: l.product_id == product)

                remaining_preorder_qty = sum(preorder_line_ids.mapped('pre_ordered_qty'))

                for presale_line_id in presale_line_ids:
                    if remaining_preorder_qty <= 0:
                        break

                    if presale_line_id.product_qty <= remaining_preorder_qty:
                        remaining_preorder_qty -= presale_line_id.product_qty
                        presale_line_id.unlink()
                    else:
                        presale_line_id.product_qty -= remaining_preorder_qty
                        remaining_preorder_qty = 0

            new_po.write({'is_presale_type': True, 'is_preorder_type': False})
        if self.is_international_pre_order:
            for order in self.order_line:
                if order.international_pre_order_qty:
                    order.product_qty = order.international_pre_order_qty
                else:
                    order.unlink()

            for product in self.order_line.mapped('product_id'):
                international_preorder_line_ids = self.order_line.filtered(lambda l: l.product_id == product)
                presale_line_ids = new_po.order_line.filtered(lambda l: l.product_id == product)

                remaining_international_preorder_qty = sum(international_preorder_line_ids.mapped('international_pre_order_qty'))

                for presale_line_id in presale_line_ids:
                    if remaining_international_preorder_qty <= 0:
                        break

                    if presale_line_id.product_qty <= remaining_international_preorder_qty:
                        remaining_international_preorder_qty -= presale_line_id.product_qty
                        presale_line_id.unlink()
                    else:
                        presale_line_id.product_qty -= remaining_international_preorder_qty
                        remaining_international_preorder_qty = 0

            new_po.write({'is_presale_type': True, 'is_international_pre_order': False})
        new_po.with_context(convert_to_presale=True).button_confirm()
        self.with_context(convert_to_presale=True).button_confirm()
        self.message_post(body=Markup(_(
                f"This pre order was confirmed and its converted to Presale:<a href=# data-oe-model='{new_po._name}' data-oe-id='{new_po.id}'>{new_po.name}</a>")))
        new_po.message_post(body=Markup(_(
                f"This presale request was created from <a href=# data-oe-model='{self._name}' data-oe-id='{self.id}'>{self.name}</a>")))
        return True

    def update_prices_after_change_date_planned(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose: update a product presale price from update button at Expected Arrival.
        """
        for order in self:
            if order.is_presale_type:
                self.env['product.product'].with_context(po=order).presale_product_price_update()
                if order.presale_rel_ids:
                    sale_ids = order.presale_rel_ids.mapped('sale_id').ids
                    po_ref = self.env['presale.purchase.rel'].search([('sale_id', 'in', sale_ids)]).mapped('purchase_id')
                    new_dates= ''
                    for po_date in po_ref:
                        if new_dates:
                            new_dates += ',' + str(po_date.date_planned.date())
                        else:
                            new_dates = str(po_date.date_planned.date())
                    sale_line_ids = order.presale_rel_ids.sale_id.order_line.filtered(
                        lambda line: line.product_id.id in order.order_line.product_id.ids)
                    if sale_line_ids:
                        for line in sale_line_ids:
                            line.tentative_arrival_date = new_dates

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose:if order are international preorder and condition are not fulfilled then raise error and not saved a po.
        """
        res = super(PurchaseOrder, self).write(vals)
        if self.is_international_pre_order and len(self.order_line) > 1:
            raise UserError(_('You can not add more product in international preorder'))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: if order are international preorder and condition are not fulfilled then raise error and not creating a po.
        """
        res = super().create(vals_list)
        for record in res:
            if record.is_international_pre_order and len(record.order_line) > 1:
                raise UserError(_('You can not add more product in international preorder'))
        return res

    def presale_price_update_as_per_price_changes(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16 { https://app.clickup.com/t/86dt7knna }
            Purpose: Update the prices for only current po products
        """
        for order in self:
            if order.is_presale_type:
                self.env['product.product'].with_context(po=order).presale_product_price_update()