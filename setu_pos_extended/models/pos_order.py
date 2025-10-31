from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    sales_team_id = fields.Many2one('crm.team', 'Sales Team')
    has_discount = fields.Boolean('Discount', default=False)

    @api.model
    def create_from_ui(self, orders, draft=False):
        """
            Author: smith@setuconsulting
            Date: 12/05/23
            Task: Migration
            Purpose: Identify the pos order has a discount
        """
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            for discount in order.lines.mapped('discount'):
                if discount > 0:
                    order.has_discount = True
        return order_ids

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['sales_team_id'] = ui_order['sales_team_id']
        return res

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if self.sales_team_id:
            vals['team_id'] = self.sales_team_id.id,
        return vals
