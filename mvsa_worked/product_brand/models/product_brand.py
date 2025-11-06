from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"
    _order = 'name'

    name = fields.Char('Brand Name', required=True, index='trigram')
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File', attachment=True)
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )


    @api.depends('product_ids')
    def _compute_products_count(self):
        """
            Authour: nidhi@setconsulting.com
            Date: 10/12/24
            Task: Migration from V16 to V18
            Purpose: This method is used to count the products per brands
        """
        for brand in self:
            brand.products_count = len(brand.product_ids)
