from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_monthly_proposal = fields.Boolean()
    is_monthly_interval_proposal = fields.Boolean()

    # def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
    #     res = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
    #     if self.is_monthly_proposal and kwargs.get('suggested_quantity'):
    #         sale_order_line = self.order_line.filtered(lambda so: so.product_id.id == product_id)
    #         sale_order_line.product_uom_qty = sale_order_line.product_id.compute_suggested_quantity()
    #         res.update({'quantity': sale_order_line.product_uom_qty})
    #     return res

    def open_wiz_from_view(self):
        # remove wizard
        view = self.env['update.so.price'].create([{'sale_order_ids': [(6, 0, self.ids)]}])
        return {
            'name': "Update Sale Order",
            'view_mode': 'form',
            'res_id': view.id,
            'view_type': 'form',
            'res_model': 'update.so.price',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }
