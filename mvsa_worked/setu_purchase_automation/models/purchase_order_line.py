from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    last_purchase_price = fields.Float(string='Last PO Price', compute='_compute_last_purchase_price', store=True)
    percentage_price_difference = fields.Float(string='% Price Difference', compute='_compute_last_purchase_price',
                                               store=True)
    igi = fields.Float(string='IGI')
    iva = fields.Float(string='Importation IVA')
    vendor_price = fields.Float(string="FOB Price")
    difference_between_vendor_price = fields.Float(string="Difference Vs FOB",
                                                   compute="_compute_difference_between_vendor_price", store=True)

    @api.depends('price_unit')
    def _compute_difference_between_vendor_price(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: to set the value of Difference Vs FOB from the unit price.
        """
        for po_line in self:
            if po_line.product_id.active:
                po_line.difference_between_vendor_price = 0
                seller_id = po_line.product_id.seller_ids.filtered(lambda x: x.partner_id == po_line.partner_id)
                if seller_id:
                    po_line.vendor_price = round(seller_id[0].price, 2)
                    if po_line.vendor_price != po_line.price_unit:
                        po_line.difference_between_vendor_price = (round(po_line.price_unit, 2) - po_line.vendor_price)

    @api.depends('product_id', 'price_unit')
    def _compute_last_purchase_price(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: to set the value of Last PO Price and % Price Difference which we put at purchase order line
        """
        for line in self:
            last_order_line = self.env['purchase.order.line'].search([
                ('product_id', '=', line.product_id.id),
                ('order_id.state', 'in', ['purchase', 'done']),
            ], order='id desc', limit=1)

            line.last_purchase_price = last_order_line.price_unit if last_order_line else 0.0
            if line.last_purchase_price:
                percentage_diff = ((line.price_unit / line.last_purchase_price) - 1) * 100
                line.percentage_price_difference = percentage_diff
            else:
                line.percentage_price_difference = 0.0

    @api.model
    def _get_date_planned(self, seller, po=False):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: not to change expected arrival if already set
        """
        res = super(PurchaseOrderLine,self)._get_date_planned(seller,po)
        res = po.date_planned if po and po.date_planned else self.order_id.date_planned if self.order_id.date_planned else self.order_id.date_order
        return res

    @api.onchange('product_id', 'price_subtotal')
    def _onchange_product_id(self):
        if self.product_id:
            self.iva = (self.price_subtotal * self.product_id.iva) / 100
            self.igi = (self.price_subtotal * self.product_id.igi) / 100
