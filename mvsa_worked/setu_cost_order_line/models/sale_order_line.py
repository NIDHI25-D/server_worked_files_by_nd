from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_price_base = fields.Float(string='Cost Base', default=0.0, digits=dp.get_precision('Product Price'))
    stock_picking_ids = fields.Many2many(comodel_name='stock.picking', string='Pickings', copy=False)

    @api.depends('product_uom')
    def _compute_purchase_price(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 05/12/24
            Task: Migration from V16 to V18
            Purpose: This method will set the price of the product and check whether its service type or not.
        """
        for line in self.filtered(lambda x: x.product_id.type != 'service'):
            line.purchase_price_base = line.product_id.standard_price
        return super(SaleOrderLine, self)._compute_purchase_price()

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.product_id.type != 'service':
            res.update({'purchase_price_base': self.purchase_price_base, 'purchase_price': self.purchase_price})
        if self.stock_picking_ids:
            res.update({'picking_ids': self.stock_picking_ids})
        return res