import datetime

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import datetime
from odoo import fields, http, SUPERUSER_ID, tools, _


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cancel'], type='http', auth="public", website=True, sitemap=False)
    def cancel_order(self, page=0, category=None, search='', ppg=False, **post):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 30/04/25
            Task: 18 Migration
            Purpose: cancel monthly proposal sale order from website
        """
        order = request.website.sale_get_order()
        order.action_cancel()
        order.unlink()
        return request.redirect("/shop/cart")

