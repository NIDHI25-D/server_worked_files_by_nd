from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import AccessError, UserError, ValidationError



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    preorder_amount = fields.Float(
        'Pre-Order Amount', required=True, digits=dp.get_precision('Product Price'), default=0.0, copy=False)
    is_preorder = fields.Boolean(string="Pre-Order", copy=False)
    pre_order_qty = fields.Float(string="Pre-Order Quantity", copy=False)

    presale_amount = fields.Float(
        'Pre-Sale Amount', required=True, digits=dp.get_precision('Product Price'), default=0.0, copy=False)
    is_presale = fields.Boolean(string="Pre-Sale", copy=False)
    pre_sale_qty = fields.Float(string="Pre-Sale Quantity", copy=False)

    preorder_notify = fields.Boolean(string="Pre-Order Notification", copy=False)
    tentative_arrival_date = fields.Char(string="Tentative Arrival", copy=False)
    is_international_preorder = fields.Boolean(string="International Preorder", copy=False)
    is_exclusive = fields.Boolean(string="Is Exclusive", copy=False,default=False)
    is_next_day_shipping = fields.Boolean(string="Next Day Shipping", copy=False)

    def unlink(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: if order are preorder and removed/unlink the order line called a method - manage_rfq_preorder_line_wise

        """
        for rec in self:
            if rec.is_preorder and rec.order_id.state in ('draft', 'sent'):
                rec.manage_rfq_preorder_line_wise(rec.order_id, from_sale_line=True, line_qty=rec.product_uom_qty)
        return super(SaleOrderLine, self).unlink()

    def manage_rfq_preorder_line_wise(self, order, from_sale_line=False, line_qty=0):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: checked if any lines are unreserved during removed the line.
        """
        po_so_rel_obj = self.env['preorder.sale.purchase.rel'].sudo()
        domain = [('sale_line_id', 'in', self.ids),
                  ('purchase_id.is_preorder_type', '!=', False),
                  ('purchase_id.state', 'in', ['draft', 'sent', 'to_approve'])]

        if from_sale_line:
            domain.append(('sale_id', '=', order.id))
            lines_to_unreserve = po_so_rel_obj.search(domain, order="id desc")
            if lines_to_unreserve and line_qty > 0:
                qty_to_unreserve = line_qty
                for rec in lines_to_unreserve:
                    if rec.preorder_qty > qty_to_unreserve:
                        rec.preorder_qty = rec.preorder_qty - qty_to_unreserve
                        qty_to_unreserve = 0
                    elif rec.preorder_qty <= qty_to_unreserve:
                        qty_to_unreserve = qty_to_unreserve - rec.preorder_qty
                        rec.preorder_qty = 0
        else:
            lines_to_unreserve = po_so_rel_obj.search(domain)
            lines_to_unreserve and lines_to_unreserve.write({'preorder_qty': line_qty})

    def _compute_price_unit(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 14/04/25
            Task: Migration to v18 from v16
            Purpose: set a presale price of a product and raise error if sale_order pricelist and configuration pricelist are same
        """
        current_website = self.env['website'].sudo().get_current_website()
        presale_pricelist = current_website.presale_pricelist
        excluded_pricelist = current_website.excluded_pricelist_id
        intl_preorder_pricelist = current_website.intl_preorder_pricelist_id
        # TASK : Next day shipping
        payment_term = self.order_id.partner_id.property_payment_term_id

        for line in self:
            if line.is_presale:
                # changes as per the task https://app.clickup.com/t/86dqj0qt6
                if line.order_id.pricelist_id.id == excluded_pricelist.id:
                    raise UserError(_('You can not add a product as presale with ' + line.order_id.pricelist_id.name))
                line.price_unit = line.product_id.presale_price
                line.order_id.pricelist_id = presale_pricelist
            elif line.is_international_preorder:
                line.order_id.pricelist_id = intl_preorder_pricelist
                return super()._compute_price_unit()
            elif line.is_next_day_shipping :
                if not payment_term:
                    raise UserError(_('Payment terms missing please contact marvelsa team'))
                if line.order_id.pricelist_id.id not in [current_website.cash_next_day_pricelist_id.id, current_website.credit_next_day_pricelist_id.id]:
                    raise UserError(_('You can not add Next day product with %s. Kindly add Next day Shipping Pricelist', line.order_id.pricelist_id.name))
                return super()._compute_price_unit()
            elif line and not line.is_preorder and not line.is_presale and not line.is_international_preorder and line.order_id.pricelist_id.id in [
                current_website.cash_next_day_pricelist_id.id, current_website.credit_next_day_pricelist_id.id]:
                    raise UserError(_('You can not add Product with %s. Kindly add other Pricelist', line.order_id.pricelist_id.name))
            else:
                return super()._compute_price_unit()

    @api.onchange('product_id')
    def _onchange_product_id_warning(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/04/25
            Task: Migration to v18 from v16
            Purpose: from sale order backed you can not add any products
        """
        res = super(SaleOrderLine, self)._onchange_product_id_warning()
        if self.product_id and self.order_id.is_presale and self.order_id.is_from_website:
            raise UserError(_('You can not add instock or preorder products'))
        return res