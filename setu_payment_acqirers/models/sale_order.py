from odoo import models, fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    monthly_installment_id = fields.Many2one('monthly.installment')
    latest_charge_stripe = fields.Char(string="Latest Charge Of Stripe", copy=False, index='trigram')

    # def _get_delivery_methods(self):
    #     """
    #         Author: siddharth.vasani@setuconsulting.com
    #         Date: 06/12/24
    #         Task: Migration to v18 from v16
    #         Purpose: To set only those Shipping Methods on the Website in which NEXT DAY SHIPPING is set otherwise it will not show any other
    #                  shipping method even though they are published only for next day shipping sale order
    #     """
    #     res = super(SaleOrder, self)._get_delivery_methods()
    #     if self.is_next_day_shipping:
    #         return self.env['delivery.carrier'].sudo().search([
    #             ('website_published', '=', True),('is_next_day_shipping','=',True)
    #         ]).filtered(lambda carrier: carrier._is_available_for_order(self))
    #     if not self.is_next_day_shipping:
    #         return self.env['delivery.carrier'].sudo().search([
    #             ('website_published', '=', True), ('is_next_day_shipping', '=', False)
    #         ]).filtered(lambda carrier: carrier._is_available_for_order(self))
    #     return res
