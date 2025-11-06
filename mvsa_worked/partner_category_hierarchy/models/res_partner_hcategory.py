# © 2017 Nedas Žilinskas <nedas.zilinskas@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo.exceptions import UserError
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class ResPartnerHCategory(models.Model):
    _name = 'res.partner.hcategory'
    _description = 'Partner Category'

    name = fields.Char(
        required=True,
    )

    parent_id = fields.Many2one(
        comodel_name='res.partner.hcategory',
        string='Parent Category',
    )

    child_ids = fields.One2many(
        comodel_name='res.partner.hcategory',
        inverse_name='parent_id',
        string='Child Categories',
    )

    partner_ids = fields.One2many(
        comodel_name='res.partner',
        inverse_name='hcategory_id',
        string='Related Partners',
    )

    pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        string='Allowed Pricelists',
    )

    inherited_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        string='Inherited Pricelists',
        compute='_compute_inherited_pricelist_ids',
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: Whenever the id will be having the same id in parent_id, it will give error.
        """
        for rec in self:
            if rec == rec.parent_id:
                raise UserError(_(
                    'Parent can not be same category!'
                ))

    def _compute_inherited_pricelist_ids(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 08/01/25
            Task: Migration from V16 to V18
            Purpose: set an inherited_pricelist_ids as per the parent category.
        """
        _logger.debug("Compute _compute_inherited_pricelist_ids method start")
        for rec in self:
            allowed_pricelist_ids = []
            hparent_id = rec.parent_id
            while hparent_id:
                allowed_pricelist_ids += hparent_id.pricelist_ids.ids
                hparent_id = hparent_id.parent_id
            rec.inherited_pricelist_ids = [(6, 0, allowed_pricelist_ids)]
        _logger.debug("Compute _compute_inherited_pricelist_ids method end")
