from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo import fields, http, tools, _
from datetime import datetime


class SetuSalesTimeDashboard(WebsiteSale):

    @http.route()
    def shop_payment_confirmation(self, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/12/24
            Task: Migration to v18 from v16
            Purpose: To write customer confirmation date
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            order.customer_confirmation_date = datetime.strftime(fields.datetime.now(),
                                                                 tools.DEFAULT_SERVER_DATETIME_FORMAT)
        return super(SetuSalesTimeDashboard, self).shop_payment_confirmation(**post)

    @http.route()
    def shop_payment_validate(self, sale_order_id=None, **post):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 27/12/24
            Task: Migration to v18 from v16
            Purpose: write customer confirmation date field.
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            order.customer_confirmation_date = datetime.strftime(fields.datetime.now(),
                                                                 tools.DEFAULT_SERVER_DATETIME_FORMAT)
        return super(SetuSalesTimeDashboard, self).shop_payment_validate(sale_order_id, **post)
