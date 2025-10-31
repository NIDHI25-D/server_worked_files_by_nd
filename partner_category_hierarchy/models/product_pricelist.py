# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo import models,api


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def write(self, vals):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: You cannot change a default price list sequence.
        """
        for rec in self:
            if rec.id == self.env.ref(
                    'partner_category_hierarchy.default_pricelist'
            ).id and 'sequence' in vals and vals['sequence'] != 0:
                raise ValidationError(_('You can not change sequence of default pricelist!'))

        return super(ProductPricelist, self).write(vals)

    def unlink(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: you cannot delete a default pricelist.
        """
        default_pl_id = self.env.ref('partner_category_hierarchy.default_pricelist').id
        for rec in self:
            if rec.id == default_pl_id:
                raise ValidationError(_('You can not delete default pricelist!'))
        return super(ProductPricelist, self).unlink()

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18 (CRM: Delivery Warehouse and Price list)
            Issue : When sale.order(& from CRM) is created than price list associated to partner_id where only visible but when quotation is created and page is reloaded than all pricelist were visible.
            Purpose: This method is to add domain in pricelist_id when quotation is created from sale.order and CRM.
        """
        if self._context.get('default_model') == 'sale_order':
            partner_obj = self.env['res.partner'].browse(self._context.get('default_partner_id'))
            ids = partner_obj.allowed_pricelists.ids
            if ids:
                domain.extend([('id', 'in', ids)])
        return super()._search(domain, offset, limit, order)