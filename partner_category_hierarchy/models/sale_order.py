from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_price_list(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: added a domain on a pricelist_id as per the selected partner.
        """
        pricelist_ids = self.partner_id.allowed_pricelists
        return {'domain': {'pricelist_id': [('id', 'in', pricelist_ids.ids)]}}
