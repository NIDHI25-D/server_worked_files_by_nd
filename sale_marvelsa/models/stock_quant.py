from odoo import fields, models
from odoo.tools.misc import format_datetime


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    def open_at_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 23/01/25
            Task: Migration to v18 from v16
            Purpose: modify the views and model, there are the changes in the path of the location of that.
        """
        active_model = self.env.context.get('active_model')
        if active_model == 'product.product':
            tree_view_id = self.env.ref('stock.view_stock_quant_tree').id
            form_view_id = self.env.ref('stock.view_stock_quant_form_editable').id
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
                'view_mode': 'list,form',
                'name': format_datetime(self.env, self.inventory_datetime),
                'res_model': 'stock.quant',
                'domain': [('create_date', '<', self.inventory_datetime)],
                'context': dict(self.env.context, to_date=self.inventory_datetime),
            }
            return action

        return super(StockQuantityHistory, self).open_at_date()
