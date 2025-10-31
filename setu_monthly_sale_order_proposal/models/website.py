# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def get_pricelist_available(self, show_visible=False):
        """
          Author: jay.garach@setuconsulting.com
          Date: 09/05/2025
          Task: Migration from V16 to V18
          Purpose:  added monthly_proposal_pricelist_id in allowed pricelist for website.
        """
        res = super(Website, self).get_pricelist_available(show_visible=show_visible)
        partner = self.env.user.partner_id
        allowed_selected_pricelist = partner.allowed_pricelists.filtered(lambda pl: pl.selectable) - partner.extra_pricelist.filtered(lambda pl: pl.selectable)
        allowed_selected_pricelist += partner.extra_pricelist.filtered(lambda pl: pl.selectable)
        if 'monthly_proposal_pricelist_id' in self.env['res.partner']._fields:
            allowed_selected_pricelist += partner.monthly_proposal_pricelist_id if partner.monthly_proposal_pricelist_id not in allowed_selected_pricelist else allowed_selected_pricelist
        sale_order_id = request.session.get('sale_order_id')
        if sale_order_id and self.env['sale.order'].sudo().browse(sale_order_id).is_presale:
            allowed_selected_pricelist = self.presale_pricelist
        if sale_order_id and self.env['sale.order'].sudo().browse(sale_order_id).is_international_preorder:
                allowed_selected_pricelist = self.intl_preorder_pricelist_id
        #  When page is refreshed for same product of NDS than it will take by default NDS pricelist but can be seen in the website
        if sale_order_id and self.env['sale.order'].sudo().browse(sale_order_id).is_next_day_shipping:
                allowed_selected_pricelist = self.env['sale.order'].sudo().browse(sale_order_id).pricelist_id
        if sale_order_id and not self.env['sale.order'].sudo().browse(sale_order_id).order_line:
                return allowed_selected_pricelist
        elif (sale_order_id and not self.env['sale.order'].sudo().browse(sale_order_id).is_presale and not self.env[
            'sale.order'].sudo().browse(sale_order_id).is_international_preorder) and not self.env[
            'sale.order'].sudo().browse(sale_order_id).is_next_day_shipping:
            matching_pricelists = partner.extra_pricelist & self.env['product.pricelist'].browse(
                [self.cash_next_day_pricelist_id.id, self.credit_next_day_pricelist_id.id])
            if matching_pricelists in allowed_selected_pricelist:
                allowed_selected_pricelist -= matching_pricelists
        return allowed_selected_pricelist