
from odoo import api, fields, models, _


class PurchaseOrderConfirmWizard(models.TransientModel):
    _name = 'purchase.order.confirm.wizard'
    _description = 'Purchase Order Confirm Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.model
    def default_get(self, fields):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/04/25
            Task: Migration to v18 from v16
            Requirement : Add the following text: En_USD -- Are you sure to confirm the purchase order with currency x?
            -- As per the flow, there was an only string : 'Are you sure?' in attribute confirm, but they need to add currency in the string,so
               need to create wizard while clicking on confirm button of PO and set the field: currency_id.
            Purpose: This method is used to set field currency_id in wizard as per the requirement
        """
        res = super(PurchaseOrderConfirmWizard, self).default_get(fields)
        if self.env['purchase.order'].browse(self._context.get('active_id')).currency_id:
            res.update({'currency_id':self.env['purchase.order'].browse(self._context.get('active_id')).currency_id.id})
        return res


    def action_confirm_purchase_order(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/04/25
            Task: Migration to v18 from v16
            Purpose: This method is used to open a wizard when user confirms order of a purchase order. This method sets a context : po_force_confirm
                     to true and then refers to button_confirm() of purchase order(setu_website_preorder)
        """
        order_id = self._context.get('active_id')
        order = self.env['purchase.order'].browse(order_id)
        return order.with_context(po_force_confirm=True).button_confirm()
