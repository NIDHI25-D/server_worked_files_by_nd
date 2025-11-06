from odoo import api, models, fields, tools, _
from odoo.addons.payment_stripe import const, utils as stripe_utils
from werkzeug.urls import url_encode, url_join, url_parse
import requests
import json
from odoo import SUPERUSER_ID

class AcquirerHyperPay(models.Model):
    _inherit = 'payment.provider'

    enable_monthly_installment = fields.Boolean(string='Enable Monthly Installment')
    monthly_installment_ids = fields.One2many('monthly.installment', 'payment_acquirer_id')



    def _stripe_get_inline_form_values(self, amount, currency, partner_id, is_validation, payment_method_sudo=None, **kwargs):
        """
               Authour:sagar.pandya@setconsulting.com
               Date: 23/04/25
               Task: 18 Migration
               Purpose:
               => update enable_monthly_installment in inline form values if monthly installment enable
        """
        res = super()._stripe_get_inline_form_values(amount,currency,partner_id,is_validation,payment_method_sudo=payment_method_sudo, **kwargs)
        if self.code == 'stripe' and self.enable_monthly_installment:
            values_dic = json.loads(res)
            values_dic.update({'enable_monthly_installment':True})
            res = json.dumps(values_dic)
        return res

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """
                 Authour: nidhi@setconsulting
                 Date: 16/07/25
                 Task: https://app.clickup.com/t/86dx4p7bg
                 Purpose:
                 => Override of payment to unlist PayUmoney providers when the currency is not INR.
          """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        for i in providers:
            # if self.env.ref('setu_payment_bbva.payment_provider_bbva').id == i.id:
            i = i.with_user(SUPERUSER_ID)
            monthly_installment_ids = i.monthly_installment_ids
            if i.enable_monthly_installment and i.monthly_installment_ids:
                sale_order_id = kwargs.get('sale_order_id', False)
                sale_order = False
                if sale_order_id:
                    sale_order = self.env['sale.order'].browse(sale_order_id)
                    pricelist_id = sale_order.pricelist_id
                    prlist_avil_in_installments = i.monthly_installment_ids.filtered(
                        lambda month_inst: month_inst.pricelist_id.id == pricelist_id.id)
                    if prlist_avil_in_installments:
                        continue
                    else:
                        providers -= i

        return providers

