# -*- coding: utf-8 -*-
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import Controller, request, route


class WebsiteSalesEXT(WebsiteSale):

    @route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """
            Author: jay@setuconsulting.com
            Date:  06/12/2024
            Task: Migration From V16 to V18
            Purpose: Public User is not able to access shop page
        """
        if request.env.user._is_public():
            if category:
                category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
                return request.redirect('/web/login?redirect=/shop/category/%s' % category.id)
            else:
                return request.redirect('/web/login')

        res = super(WebsiteSalesEXT, self).shop(page=page, category=category, search=search, min_price=min_price,
                                                max_price=max_price, ppg=ppg, **post)
        return res

    @route()
    def product(self, product, category='', search='', **kwargs):
        """
            Author: jay@setuconsulting.com
            Date: 06/12/2024
            Task: Migration From V16 to V18
            Purpose: Public User is not able to access shop page
        """
        if request.env.user._is_public():
            if product:
                return request.redirect('/web/login?redirect=/shop/%s' % product.id)
            else:
                return request.redirect('/web/login')
        return super(WebsiteSalesEXT, self).product(product=product, category=category, search=search, **kwargs)
