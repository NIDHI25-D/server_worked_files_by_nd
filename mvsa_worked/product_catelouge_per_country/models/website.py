# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request
from odoo.osv import expression

class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 17-01-2024
        Task:  [1478] Product Catalog per country
        Purpose: This method will give products and product types as per brands and as per the product type respectively and added to the controller.
        """
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['products_only']:
            brand_list = request.httprequest.args.getlist('brand')
            brand_list = [int(i) for i in brand_list]
            product_type_list = request.httprequest.args.getlist('product_type')
            product_type_list = [int(i) for i in product_type_list]
            domain = []
            if brand_list:
                domain.extend([('product_brand_id', 'in', brand_list)])
            if product_type_list:
                domain.extend([('product_type_marvelsa', 'in', product_type_list)])
            result[0]['base_domain'][0].extend(domain)
        return result

    def sale_product_domain(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 17-01-2024
        Task: [1478] Product Catalog per country
        Purpose: This method is used to excluded the products from the countries mentioned in the brand
        """
        res = super(Website, self).sale_product_domain()
        brands_product_excluded = self.env['product.brand'].sudo().search(
            [('enable_exclude_products', '!=', False), ('country_ids', 'in', self.env.user.country_id.ids)])
        if brands_product_excluded:
            res.extend([('product_brand_id', 'not in', brands_product_excluded.ids)])
        return res
