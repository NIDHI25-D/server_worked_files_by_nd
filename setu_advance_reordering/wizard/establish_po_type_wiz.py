from odoo import fields, models, api


class EstablishPOTypeWiz(models.TransientModel):
    _name = 'establish.po.type.wiz'
    _description = "Establish PO Type"

    purchase_order_type = fields.Selection(
        string='Purchase Order Type',
        selection=[('in_stock', 'In Stock'),
                   ('pre_sale', 'Pre Sale'),
                   ('pre_order', 'Pre Order')],
        required=True)

    def action_establish_po_type(self):
        active_ids = self._context.get('active_ids')
        purchase_order_type = self.purchase_order_type
        for active_id in active_ids:
            advance_reorder_orderprocess = self.env['advance.reorder.orderprocess'].browse(active_id)
            if advance_reorder_orderprocess.state == 'draft':
                advance_reorder_orderprocess.write({
                    'purchase_order_type': purchase_order_type,
                })

