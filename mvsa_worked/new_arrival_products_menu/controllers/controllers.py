# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request



class WebsiteSaleExt(WebsiteSale):

    def _get_search_options(self, **post):
        options = super()._get_search_options(**post)
        new_arrival = request.context.get('newArrivals')
        options.update({
            'new_arrival': new_arrival
        })
        return options

    @http.route(['''/newarrivals/shop''',
                 '''/newarrivals/shop/page/<int:page>''',
                 '''/newarrivals/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
                 '''/newarrivals/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
                 ], type='http', auth="public", website=True)
    def newarrivals(self,page=0, **post):
        if request.env.user._is_public():
            return request.redirect('/web/login')
        context = request.env.context.copy()
        context.update({'newArrivals':1})
        request.update_context(**context)
        new_arr_shop = self.shop(page=page,**post)
        if request.env.context.get('no_newArrivals_products'):
            new_arr_shop.qcontext.update({'bins':[],'products':False,'search_count':0})
            new_arr_shop.qcontext['pager']['page_count'] =0
        new_arr_shop.qcontext['pager']['page']['url'] = '/newarrivals'+new_arr_shop.qcontext['pager']['page']['url']
        new_arr_shop.qcontext['pager']['page']['num'] = page

        new_arr_shop.qcontext['pager']['page_start']['url'] = '/newarrivals'+new_arr_shop.qcontext['pager']['page_start']['url']
        new_arr_shop.qcontext['pager']['page_start']['num'] = page

        new_arr_shop.qcontext['pager']['page_previous']['url'] = '/newarrivals' + new_arr_shop.qcontext['pager']['page_previous']['url']
        new_arr_shop.qcontext['pager']['page_previous']['num'] = page

        new_arr_shop.qcontext['pager']['page_next']['url'] = '/newarrivals' +new_arr_shop.qcontext['pager']['page_next']['url']
        new_arr_shop.qcontext['pager']['page_next']['num'] = page

        new_arr_shop.qcontext['pager']['page_end']['url'] = '/newarrivals' + new_arr_shop.qcontext['pager']['page_end']['url']
        new_arr_shop.qcontext['pager']['page_end']['num'] = page

        new_arr_shop.qcontext['pager']['pages'][0]['url'] = '/newarrivals' + new_arr_shop.qcontext['pager']['pages'][0]['url']
        num=1

        for pc in range(1,len(new_arr_shop.qcontext['pager']['pages'])):
            new_arr_shop.qcontext['pager']['pages'][num]['url'] = '/newarrivals' +new_arr_shop.qcontext['pager']['pages'][num]['url']
            num = num+1

        new_arr_shop.qcontext.update({'new_arrivals': True})
        return new_arr_shop