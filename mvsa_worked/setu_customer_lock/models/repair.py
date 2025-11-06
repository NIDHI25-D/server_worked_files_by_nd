from odoo.exceptions import UserError

from odoo import models, api, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    @api.model_create_multi
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose:This method will unable to create a repair order if the customer is locked.
                    :param vals: Repair Order value dictionary.
                    :return: Repair Order object.
        """
        for val in vals:
            partner = val.get('partner_id', False)
            partner = partner and self.env['res.partner'].sudo().browse(partner) or False
            if partner and partner.is_customer_locked and not self._context.get('action_cancel_of_repair_order', False):
                raise UserError(
                    _("Unable to process the order as this customer has been locked, please contact the credit and collection area for clarification."))
        return super(RepairOrder, self).create(vals)

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose:This method will unable to select a locked customer in the repair order.
                    :param vals: repair Order update value dictionary.
                    :return: It will return True or False.
        """
        partner = vals.get('partner_id', False)
        partner = partner and self.env['res.partner'].sudo().browse(partner) or False
        if partner and partner.is_customer_locked and not self._context.get('website_id', False) and not self._context.get(
                'action_cancel_of_repair_order', False):
            raise UserError(
                _("Unable to process the order as this customer has been locked, please contact the credit and collection area for clarification."))
        return super(RepairOrder, self).write(vals)

    def action_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: Added new context
        """
        context = self._context.copy() or {}
        context.update({'action_cancel_of_repair_order': True})
        return super(RepairOrder, self.with_context(context)).action_cancel()
