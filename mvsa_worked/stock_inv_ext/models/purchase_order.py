from odoo import models, api,fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    landed_cost_count = fields.Integer('Landed cost count', compute='_compute_landed_cost_count')

    @api.depends('amount_total')
    def _compute_landed_cost_count(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: count of total number of landed cost record that are related PO.
        """
        landed_cost_count = len(self.env['stock.landed.cost'].search([('related_purchase_orders', 'in', self.ids)]))
        if landed_cost_count == 0:
            self.landed_cost_count = 0
        self.landed_cost_count = landed_cost_count

    @api.depends('name')
    def name_get(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: return purchase order id and name only when stock landed cost view is display
        """
        res = super(PurchaseOrder, self).name_get()
        if self._context.get('params') and self._context.get('params', {}).get('model') == 'stock.landed.cost':
            res = []
            for po in self:
                name = po.name
                res.append((po.id, name))
        return res

    def action_view_landed_costs(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: create an action for showing related landed cost.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock_landed_costs.action_stock_landed_cost")
        domain = [('related_purchase_orders', 'in', self.ids)]
        views = [(self.env.ref('stock_landed_costs.view_stock_landed_cost_tree2').id, 'list'), (False, 'form'),
                 (False, 'kanban')]
        return dict(action, domain=domain, views=views)
