from odoo import api, fields, models, _
import datetime
import logging
_logger = logging.getLogger("delete_sale_orders_from_abandoneds_carts")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def cron_delete_sale_orders_from_abandoneds_carts(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 11/03/25
            Task: Migration to v18 from v16
            Purpose: delete abandoneds_sale_orders as per the default values from today to past days as per the field Days Configure for Abondends carts deleting cron in setting.
        """
        abondend_cart_deleting_days_value = int(self.env['ir.config_parameter'].sudo().get_param('website_marvelsa.abondend_cart_deleting_days')) or 0
        todays_date = datetime.datetime.today()
        days = datetime.timedelta(abondend_cart_deleting_days_value)
        keep_sale_order_safe_date = todays_date - days
        abandoneds_sale_orders = self.env['sale.order'].sudo().search(
            [('is_abandoned_cart', '=', True), ('date_order', '<', keep_sale_order_safe_date)])
        _logger.info(
            f"Total abandoneds sale orders deleting before the days==>{abondend_cart_deleting_days_value}, Sale orders==> {abandoneds_sale_orders}")
        if abandoneds_sale_orders:
            try:
                for orders in abandoneds_sale_orders:
                    orders.sudo().action_cancel()
                    _logger.info("Sale order %s is going to deleted" % orders.name)
                    orders.sudo().unlink()
                _logger.info("Successfully deleted all above abandoneds sale orders")
            except Exception as e:
                    _logger.info("Error occurs during the delete abandoneds sale orders :- %s" % e)
        else:
            _logger.info("There is not found any sale orders before your configured days")
