# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request

from odoo.addons.marvelfields.controllers.main import WebsiteSaleExt
import json


class SearchCompetiblesWebsiteSaleExt(WebsiteSaleExt):

    def _get_shop_domain(self, search, category, attrib_values, search_in_description=True):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 08/05/23
        Task: [1478] Product Catalog per country
        Purpose: This method will search for the domain of brand. It will give the products as per brand as well as types as per the product types
        """
        domain = super(SearchCompetiblesWebsiteSaleExt, self)._get_shop_domain(search, category, attrib_values, search_in_description)
        brand_list = request.httprequest.args.getlist('brand')
        if brand_list:
            brand_list = ','.join([str(id) for id in brand_list]).split(',')
        brand_list = [int(i) for i in brand_list]

        product_type_list = request.httprequest.args.getlist('product_type')
        if product_type_list:
            product_type_list = ','.join([str(id) for id in product_type_list]).split(',')
        product_type_list = [int(i) for i in product_type_list]
        if brand_list:
            domain.extend([('product_brand_id', 'in', brand_list)])
        if product_type_list:
            domain.extend([('product_type_marvelsa', 'in', product_type_list)])
        return domain


class ProductCatelougePerCountry(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 16-01-2025
        Task: [1478] Product Catalog per country
        Purpose: This method will update context active brand and product type in shop page
        :param page:
        :param category:
        :param search:
        :param ppg:
        :param post:
        :return: Dictionary
        """
        brand_list = request.httprequest.args.getlist('brand')
        brand_list = [int(i) for i in brand_list]
        product_type_list = request.httprequest.args.getlist('product_type')
        product_type_list = [int(i) for i in product_type_list]
        if brand_list:
            post['brand'] = brand_list
        if product_type_list:
            post['product_type'] = product_type_list
        request.update_context(from_product_loading_page=True, bin_size=True)
        res = super(ProductCatelougePerCountry, self).shop(page, category, search, min_price, max_price, ppg, **post)
        res.qcontext.update({
            'active_brand': brand_list,
            'active_product_type': product_type_list,
        })
        return res
