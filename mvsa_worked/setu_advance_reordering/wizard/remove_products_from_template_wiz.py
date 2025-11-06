from odoo import fields, models, api


class RemoveProductsFromTemplateWiz(models.TransientModel):
    _name = 'remove.products.from.template.wiz'
    _description = "Remove Products From Template"

    reorder_planner_ids = fields.Many2many('advance.reorder.planner', string='Reorder Planner Name', domain=[('state', '=','draft')])

    def action_remove_products_from_planner(self):
        for rec in self.reorder_planner_ids:
            if rec.state == 'draft':
                active_id = self._context.get('active_id')
                product_id = self.env['product.product'].browse(active_id)
                filtered_products = rec.product_ids.filtered(lambda prod: prod.id == product_id.id)
                if filtered_products:
                    rec.product_ids = [(3, filtered_products.id, 0)]
