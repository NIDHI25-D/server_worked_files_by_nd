from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.osv import expression
from odoo import SUPERUSER_ID
from odoo.http import request, route

class WebsiteSaleExt(WebsiteSale):

    def _get_shop_domain(self, search, category, attrib_values, search_in_description=True):
        """
            Author: jay.garach@setuconsulting.com
            Date: 26/12/24
            Task: Migration from V16 to V18
            Purpose: This method will give the description and other details as per the product/category searched in the search box of website
        """
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if request.env['ir.module.module'].with_user(SUPERUSER_ID).search(
                        [('name', '=', 'marvelfields')]).state == 'installed':
                    subdomains.append([('compatible_ids', 'ilike', srch)])
                if search_in_description:
                    subdomains.append([('description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)

    def _get_search_order(self, post):
        """
          Author: jay.garach@setuconsulting.com
          Date: 00/00/00
          Task: Migration from V16 to V18
          Purpose: This Method is sorting the product into website order screen.
        """
        order = post.get('order') or 'website_sequence desc'
        if post.get('order'):
            return 'is_published desc,product_type_marvelsa asc,%s, id desc' % order
        else:
            return 'is_published desc, %s, id desc' % order
