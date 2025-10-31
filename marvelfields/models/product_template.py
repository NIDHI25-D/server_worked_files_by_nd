# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.tools.translate import html_translate
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    compatible_ids = fields.Many2many(
        'marvelfields.compatible', 'marvelfields_compatible_rel',
        'src_id', 'dest_id',
        string='Compatibles')
    compatible_product_ids = fields.Many2many(
        'product.template', 'product_compatible_rel', 'src_id', 'dest_id',
        string='Compatible', help="Optional Products are suggested "
                                  "whenever the customer hits *Add to Cart* (cross-sell strategy, "
                                  "e.g. for computers: warranty, software, etc.).")
    length = fields.Float(string="Length", compute='_compute_measures')
    whidth = fields.Float(string="Whidth", compute='_compute_measures')
    high = fields.Float(string="High", compute='_compute_measures')
    temporary_id = fields.Many2one('product.temporary', string="Season")
    is_on_catalogue = fields.Boolean(string="Is on Catalogue")
    discontinued = fields.Boolean(string="Discontinued")
    product_type_marvelsa = fields.Selection([
        ('1', 'Product Done'),
        ('2', 'Accessory'),
        ('3', 'Spare Part'),
        ('4', 'Spare Part Service')])
    category_manager = fields.Many2one('res.users', string='Category Manager', domain="[('share','=',False)]")
    origin_id = fields.Many2one('origin.database', string='Origin')
    seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors', depends_context=('company',),
                                 copy=True)
    descriptive_website_products = fields.Html(
        'Website description', translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False, sanitize_form=False)

    @api.depends('product_variant_ids', 'product_variant_ids.length', 'product_variant_ids.whidth',
                 'product_variant_ids.high')
    def _compute_measures(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 01/01/25
            Task: Migration from V16 to V18
            Purpose: set a length, whidth and high
        """
        _logger.debug("Compute _compute_measures method start")
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.length = template.product_variant_ids.length
            template.whidth = template.product_variant_ids.whidth
            template.high = template.product_variant_ids.high
        for template in (self - unique_variants):
            template.length = 0.0
            template.whidth = 0.0
            template.high = 0.0
        _logger.debug("Compute _compute_measures method end")

    @api.constrains('list_price', 'seller_ids')
    def check_sale_price(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18
            Purpose: raise a validation if no seller is found and if sale price is not grater than zero
        """
        if self._context.get('install_module'):
            pass
        else:
            for record in self.filtered(lambda x: x.type != 'service'):
                if record.list_price <= 0.00:
                    raise ValidationError(_('Sales price should be greater than zero.'))
                if record.seller_ids:
                    for supplier in record.seller_ids:
                        if supplier.price <= 0:
                            raise ValidationError(_('Price in supplier information should be greater than zero.'))
                if not record.seller_ids or len(record.seller_ids) == 0:
                    raise ValidationError(_('Please add supplier information in product.'))