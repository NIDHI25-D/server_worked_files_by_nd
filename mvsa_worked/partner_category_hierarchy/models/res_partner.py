# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hcategory_id = fields.Many2one(
        comodel_name='res.partner.hcategory',
        string='Category',
    )
    allowed_pricelists = fields.Many2many(comodel_name='product.pricelist', compute='_compute_allowed_pricelists')
    extra_pricelist = fields.Many2many('product.pricelist', string='Extra Pricelist',
                                       domain="[('id', 'not in', allowed_pricelists)]")

    def open_partner_category(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: used in module website_sale_pricelist_visibility
                    Visibility of Price lists is managed on Parent Category Used in module website_sale_pricelist_visibility.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner.hcategory',
            'view_mode': 'form',
            'res_id': self.hcategory_id.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True}}
        }

    @api.depends('hcategory_id', 'parent_id')
    def _compute_allowed_pricelists(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: set an allowed price list as per the hcateegory of partner.
        """
        _logger.debug("Compute _compute_allowed_pricelists method start")
        default_pl_id = self.env.ref('partner_category_hierarchy.default_pricelist').id
        for rec in self:
            if rec.parent_id:
                rec.hcategory_id = rec.parent_id.hcategory_id
                rec.allowed_pricelists = [
                    (6, 0, [default_pl_id] + rec.hcategory_id.pricelist_ids.ids +
                     rec.hcategory_id.inherited_pricelist_ids.ids),
                ]

            else:
                rec.allowed_pricelists = [
                    (6, 0, [default_pl_id] + rec.hcategory_id.pricelist_ids.ids +
                     rec.hcategory_id.inherited_pricelist_ids.ids),
                ]
        _logger.debug("Compute _compute_allowed_pricelists method end")
