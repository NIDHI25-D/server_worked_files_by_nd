from odoo.http import request
from odoo import http, _
from odoo.exceptions import ValidationError

from odoo.addons.website_sale.controllers import payment as website_sale_controller
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.portal import PaymentPortal


class PaymentPortal(website_sale_controller.PaymentPortal):
    @http.route()
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """
        @Author: siddharth.vasani@setuconsulting.com
        @Date : 03/03/2024
        @Purpose : This method will use if payment voucher order
        :param order_id:
        :param access_token:
        :param kwargs:
        :return:
        """
        res = super().shop_payment_transaction(order_id, access_token, **kwargs)
        order = request.env['sale.order'].sudo().browse(order_id)
        if order and kwargs.get('is_payment_voucher_warning'):
            order.is_payment_voucher_warning = kwargs.get('is_payment_voucher_warning')
        return res

# class AddKwrgs(payment_portal.PaymentPortal):
#    Remove this part because both modules define their own static _validate_transaction_kwargs, the last one will loaded.
#    ADDED this part logic in setu_payment_acqirers module
#     @staticmethod
#     def _validate_transaction_kwargs(kwargs, additional_allowed_keys=()):
#         """
#         @Author: siddharth.vasani@setuconsulting.com
#         @Date : 03/03/2024
#         @Purpose : This method is used to pass is_payment_voucher_warning for validate transaction in kwargs
#         :param kwargs:
#         :param additional_allowed_keys:
#         :return: None
#         """
#         res = payment_portal.PaymentPortal._validate_transaction_kwargs(kwargs, additional_allowed_keys=(
#             'is_payment_voucher_warning',))
#         return res