from odoo import fields, models, api, _
from odoo.tools import float_compare
from operator import itemgetter
from odoo.exceptions import ValidationError, UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    follow_vendor_moq_rule = fields.Boolean('Follow Vendor Minimum Quantity Rule ?', default=False)
    capping_qty = fields.Float("Highest sales qty level", help="""
    Ignore all sales if the sales qty is above the defined highest level in the reordering average sales calculation
    """)
    update_orderpoint = fields.Boolean("Update Order Point?", default=True,
                                       help="By configuring this by True, order points of this product will be "
                                            "automatically updated.")
    can_be_used_for_advance_reordering = fields.Boolean(string="Can Be Used For Advance Reordering?", default=True,
                                                        store=True)
    stock_requested_by_commercial = fields.Integer(string="Stock Requested By Commercial")
    reorder_planner_template_ids = fields.Many2many("advance.reorder.planner", string="Add to planner template")

    @api.onchange('can_be_used_for_advance_reordering')
    def _onchange_can_be_used_for_advance_reordering_variant(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 08/01/25
            Task: AR’s followship enhancements(migration from 16 to 18).
            Purpose: using this method remove the product where Can Be Used For Advance Reordering? field are false in product variant also remove from demand calculation.
        """
        for record in self:
            if not record.can_be_used_for_advance_reordering:
                advance_reorder = self.env['advance.reorder.orderprocess'].search(
                    [('product_ids', 'in', [record._origin.id if record._origin else record.id]),
                     ('state', 'in', ['draft', 'inprogress'])])

                if advance_reorder:
                    filtered_product = advance_reorder.product_ids.filtered(lambda x: x == record._origin)
                    if filtered_product:
                        advance_reorder.product_ids = [(3, filtered_product.id, 0)]
                    advance_reorder_with_line_ids = advance_reorder.filtered(lambda line: line.line_ids)
                    if advance_reorder_with_line_ids:
                        filtered_product_for_demand_calculation = advance_reorder_with_line_ids.line_ids.filtered(
                            lambda x: x.product_id == record._origin)
                        if filtered_product_for_demand_calculation:
                            advance_reorder_with_line_ids.line_ids = [
                                (3, filtered_product_for_demand_calculation.ids, 0)]
    
    def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, ordered_by='price_discounted', params=False):
        """
                added by: Aastha Vora | On: Oct - 11 - 2024 | Task: 998
                use: Always sort sellers by discounted price but another field can take the primacy through the `ordered_by` param.
        """
        sort_key = itemgetter('price_discounted', 'sequence', 'id')
        if ordered_by != 'price_discounted':
            sort_key = itemgetter(ordered_by, 'price_discounted', 'sequence', 'id')

        sellers = self._get_filtered_sellers(partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id, params=params)
        res = self.env['product.supplierinfo']
        for seller in sellers:
            if not res or res.partner_id != seller.partner_id:
                res |= seller
        sort_key = self.env.context.get("sory_by", sort_key if sort_key else 'sequence')
        if sort_key == 'price' and res:
            company_id = self.env.context.get("op_company")
            return res.sorted(key=lambda x: x.currency_id._convert(x.price, company_id.currency_id, company_id, date))[
                   :1]
        else:
            return res and res.sorted(sort_key)[:1]

    def _get_filtered_sellers(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
        """
                 added by: Aastha Vora | On: Oct - 11 - 2024 | Task: 998
                 use: used to filter sellers.
        """
        self.ensure_one()
        if date is None:
            date = fields.Date.context_today(self)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        sellers_filtered = self._prepare_sellers(params)
        if self.env.context.get('force_company'):
            sellers_filtered = sellers_filtered.filtered(
                lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
        else:
            sellers_filtered = sellers_filtered.filtered(
                lambda s: not s.company_id or s.company_id.id == self.env.company.id)
        sellers = self.env['product.supplierinfo']
        for seller in sellers_filtered:
            # Set quantity in UoM of seller
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.partner_id not in [partner_id, partner_id.parent_id]:
                continue
            if quantity is not None and float_compare(quantity_uom_seller, seller.min_qty,
                                                      precision_digits=precision) == -1:
                continue
            if seller.product_id and seller.product_id != self:
                continue
            sellers |= seller
        return sellers

    def action_remove_from_ar_template(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 08/01/25
            Task: migration from 16 to 18.
            Purpose: open wizard to remove product from AR template as per the AR enhancement
        """
        return {
                'name': 'Remove From AR Template',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'remove.products.from.template.wiz'
            }

    # no needed more in 18 and made it as per the 16.
    # def write(self, vals):
    #     """
    #         Author: siddharth.vasani@setuconsulting.com
    #         Date: 15/01/25
    #         Task: Migration to v18 from v16
    #         Purpose: to not add or remove validate planner as maintain the flow of reorder.
    #     """
    #     if 'reorder_planner_template_ids' in vals:
    #         planner_obj = self.env['advance.reorder.planner']
    #         for planner in vals.get('reorder_planner_template_ids'):
    #             planner_id = planner_obj.browse(planner[1])
    #             if planner_id.state != 'draft':
    #                 raise ValidationError(("You cannot add/remove those planner records which is in draft state."
    #                                    ))
    #     return super(ProductProduct, self).write(vals)


