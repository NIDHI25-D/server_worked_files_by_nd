from odoo import models, api, fields, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pre_ordered_qty = fields.Float(string="Pre-ordered", default=0,
                                   store=False, compute="_calculate_preorder_quantity",
                                   compute_sudo=True, copy=False)

    preorder_rel_ids = fields.One2many("preorder.sale.purchase.rel", 'purchase_line_id',
                                       string="Pre-order Details",
                                       copy=False,domain="[]")

    pre_sale_qty = fields.Float(string="Pre-Sale", default=0,
                                   store=False, compute="_calculate_presale_quantity",
                                   compute_sudo=True, copy=False)

    presale_rel_ids = fields.One2many("presale.purchase.rel", 'purchase_line_id',
                                       string="Pre-sale Details",
                                       copy=False)

    international_pre_order_qty = fields.Float(string="International Pre-Order", default=0,
                                store=False, compute="_calculate_international_preorder_qty",
                                compute_sudo=True, copy=False)

    international_preorder_rel_ids = fields.One2many("international.preorder.sale.purchase.rel", 'purchase_line_id',
                                                     string="International Pre-order Details",
                                                     copy=False,)


    def _calculate_preorder_quantity(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: Set Pre-ordered qty from corresponding orders.
        """
        self.pre_ordered_qty = 0
        for record in self.filtered(lambda x: x.order_id and x.order_id.is_preorder_type):
            rel_ids = record.preorder_rel_ids.filtered(lambda x: x.pre_order_state!='cancel' and x.preorder_qty > 0)
            record.pre_ordered_qty = rel_ids and sum(rel_ids.filtered(lambda x: x.sale_id.state not in ('cancel')).mapped('preorder_qty')) or 0

    def _calculate_presale_quantity(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: Set Pre-Sale qty from corresponding orders.
        """
        self.pre_sale_qty = 0
        for record in self.filtered(lambda x: x.order_id and x.order_id.is_presale_type):
            rel_ids = record.presale_rel_ids.filtered(lambda x: x.pre_sale_state!='cancel' and x.presale_qty > 0)
            record.pre_sale_qty = rel_ids and sum(rel_ids.filtered(lambda x: x.sale_id.state not in ('cancel')).mapped('presale_qty')) or 0

    def _calculate_international_preorder_qty(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: Set International Pre-Order qty from corresponding orders.
        """
        self.international_pre_order_qty = 0
        for record in self.filtered(lambda x: x.order_id and x.order_id.is_international_pre_order):
            rel_ids = record.international_preorder_rel_ids.filtered(lambda x: x.international_pre_order_state!='cancel' and x.international_preorder_qty > 0)
            record.international_pre_order_qty = rel_ids and sum(rel_ids.filtered(lambda x: x.sale_id.state not in ('cancel')).mapped('international_preorder_qty')) or 0

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 16/04/25
            Task: Migration to v18 from v16
            Purpose: raise an error if conditions are not fulfilled.
        """
        qty_in_vals = 'product_qty' in vals
        qty = qty_in_vals and vals.get('product_qty', 0) or 0
        for record in self:
            if record.order_id.is_preorder_type and qty_in_vals and qty < record.pre_ordered_qty:
                raise UserError("You can not order less quantities then the pre-ordered quantities for the following "
                              "product,\n%s" % record.product_id.name)
            if record.order_id.is_presale_type and qty_in_vals and qty < record.pre_sale_qty:
                raise UserError("You can not order less quantities then the pre-sale quantities for the following "
                              "product,\n%s" % record.product_id.name)
            if record.order_id.is_international_pre_order and qty_in_vals and qty < record.international_pre_order_qty:
                raise UserError("You can not order less quantities then the pre-order quantities for the following "
                              "product,\n%s" % record.product_id.name)
        return super(PurchaseOrderLine, self).write(vals)

    def unlink(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose: called the method when removed/unlink order line - check_preorder_po_line_unlink_status()
        """
        self.check_preorder_po_line_unlink_status()
        return super(PurchaseOrderLine, self).unlink()

    def check_preorder_po_line_unlink_status(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose: if po's quantity are use and creates a so of this then not cancelling and raise the error as per the condition.
        """
        for record in self:
            if not record.order_id.is_preorder_type and not record.order_id.is_presale_type:
                continue
            so_rel_ids = record.mapped('preorder_rel_ids')
            current_order_lines = so_rel_ids and so_rel_ids.filtered(lambda x: x.preorder_qty > 0) or False
            so_prerel_ids = record.mapped('presale_rel_ids')
            current_presale_lines = so_prerel_ids and so_prerel_ids.filtered(lambda x: x.presale_qty > 0) or False
            if current_order_lines:
                current_order_lines_str = "\n".join(map(str, current_order_lines.mapped('sale_id').mapped('name')))
                raise UserError("You can't cancel/delete this order/line as some of the products of this Purchase Order "
                              "is already pre-ordered in few Sale Orders,\n%s" % current_order_lines_str)
            if current_presale_lines:
                current_order_lines_str1 = "\n".join(map(str, current_presale_lines.mapped('sale_id').mapped('name')))
                raise UserError("You can't cancel/delete this order/line as some of the products of this Purchase Order "
                              "is already pre-sale in few Sale Orders,\n%s" % current_order_lines_str1)

    @api.onchange('product_id')
    def onchange_product_id_for_presale(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: Raise an error while creating a presale if added product has no import factor level id
        """
        for line in self:
            if line.order_id.is_presale_type:
                if line.product_id and not line.product_id.import_factor_level_id:
                    raise UserError("Please Add a import level factor on a product")
                if line.product_id and not line.product_id.competition_level_id:
                    raise UserError("Please Add a competition level on a product")
            if line.order_id.is_international_pre_order:
                if line.product_id and line.product_id.available_for_presale:
                    raise UserError("This Product is Already Available For Presale")
                if line.product_id and line.product_id.available_for_preorder:
                    raise UserError("This Product is Already Available For Preorder")
