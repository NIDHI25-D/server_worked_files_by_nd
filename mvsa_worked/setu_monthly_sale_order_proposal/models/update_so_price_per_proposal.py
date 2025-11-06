from odoo import models, fields, _
from odoo.exceptions import UserError


class UpdateOrderPrice(models.TransientModel):
    _name = 'update.so.price'
    _description = 'Update So Price'

    pricelist_id = fields.Many2one('product.pricelist')
    sale_order_ids = fields.Many2many('sale.order', 'update_so_sale_order_rel', 'update_so_id', 'sale_id')

    def update_so_price(self):
        # remove wizard
        orders = self.sale_order_ids
        for ord in orders:
            if ord.state == 'draft':
                ord.pricelist_id = self.pricelist_id.id

                ord.update_prices()
