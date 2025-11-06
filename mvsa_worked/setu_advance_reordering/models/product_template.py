from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    can_be_used_for_advance_reordering = fields.Boolean(string="Can Be Used For Advance Reordering?", default=True,
                                                        store=True)

    # @api.onchange('can_be_used_for_advance_reordering')
    # def _onchange_can_be_used_for_advance_reordering_template(self):
    #     """
    #         Author: Siddharth@setuconsulting
    #         Date: 12/09/23
    #         Task: AR’s followship enhancements.
    #         Purpose: using this method remove the product where Can Be Used For Advance Reordering? field are false in product template also remove from demand calculation.
    #     """
    #     for record in self:
    #         if not record.can_be_used_for_advance_reordering:
    #             advance_reorder = self.env['advance.reorder.orderprocess'].search([('product_ids.product_tmpl_id', 'in', [record._origin.id if record._origin else record.id]), ('state', 'in', ['draft', 'inprogress'])])
    #
    #             if advance_reorder:
    #                 filtered_product = advance_reorder.product_ids.filtered(lambda x: x.product_tmpl_id == record._origin)
    #
    #                 if filtered_product:
    #                     advance_reorder.product_ids = [(3, filtered_product.id, 0)]
    #                     advance_reorder_with_line_ids = advance_reorder.filtered(lambda line: line.line_ids)
    #                     if advance_reorder_with_line_ids:
    #                         filtered_product_for_demand_calculation = advance_reorder_with_line_ids.line_ids.filtered(lambda x: x.product_id.product_tmpl_id == record._origin)
    #                         if filtered_product_for_demand_calculation:
    #                             advance_reorder_with_line_ids.line_ids = [
    #                                 (3, filtered_product_for_demand_calculation.ids, 0)]

