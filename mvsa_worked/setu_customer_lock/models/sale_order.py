from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model_create_multi
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will unable to create a sale order if the customer is locked.
                     :param vals: Sale Order value dictionary.
                     :return: Sale Order object.
        """
        for val in vals:
            partner = val.get('partner_id', False)
            partner = partner and self.env['res.partner'].sudo().browse(partner) or False
            if partner and partner.is_customer_locked and not self._context.get('action_cancel_of_sale_order', False) and not val.get('meli_order_id'):
                raise UserError(_("The client is blocked, please contact the credit and collection area for clarification"))
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will unable to select a locked customer in the sale order.
                     :param vals: Sale Order update value dictionary.
                     :return: It will return True or False.
        """
        partner = vals.get('partner_id', False)
        partner = partner and self.env['res.partner'].sudo().browse(partner) or False
        if partner and partner.is_customer_locked and not self._context.get('website_id', False) and not self._context.get(
                'action_cancel_of_sale_order', False):
            raise UserError(_("The client is blocked, please contact the credit and collection area for clarification"))
        return super(SaleOrder, self).write(vals)

    def action_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: Added new context
        """
        context = self._context.copy() or {}
        context.update({'action_cancel_of_sale_order': True})
        return super(SaleOrder, self.with_context(context)).action_cancel()
