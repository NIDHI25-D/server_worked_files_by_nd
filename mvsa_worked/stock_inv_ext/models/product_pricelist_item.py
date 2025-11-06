from odoo import fields, models, _, api
from markupsafe import Markup


class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.model
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 13/03/25
            Task: Migration to v18 from v16
            Purpose: Used for see the history in price-list.
        """
        res = super(PricelistItem, self).create(vals)
        pricelist_id = self.env['product.pricelist'].browse(res.pricelist_id.id)
        lst3 = [(p.name, str(p.min_quantity), str(p.price), str(p.date_start), str(p.date_end)) for p in res]
        add_new_line = ""
        for order in lst3:
            add_new_line += _("%s ") % (' | '.join(order)) + "<br>"
        pricelist_id.message_post(body=Markup(_(f" New Line:- <br>{add_new_line}")))
        return res
