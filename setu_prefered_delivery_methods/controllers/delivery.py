from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route


class Delivery(WebsiteSale):

    @route('/shop/set_delivery_method', type='json', auth='public', website=True)
    def shop_set_delivery_method(self, dm_id=None, **kwargs):
        """
              Author: jay.garach@setuconsulting.com
              Date: 03/01/25
              Task: Migration from V16 to V18
              Purpose: setting up shipping_carrier_id as per order from web.
        """
        order_sudo = request.website.sale_get_order()
        if order_sudo and kwargs and kwargs.get('shipping_carrier_id'):
            shipping_carrier_id = False
            if kwargs and kwargs.get('shipping_carrier_id'):
                shipping_carrier_id = int(kwargs['shipping_carrier_id']) or False
            if shipping_carrier_id and order_sudo:
                order_sudo.shipping_carrier_id = shipping_carrier_id
            return self._order_summary_values(order_sudo, **kwargs)
        else:
            return super(Delivery, self).shop_set_delivery_method(dm_id=dm_id, **kwargs)

