# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SetuMiraklPaymentGateway(models.Model):
    _name = "setu.mirakl.payment.gateway"
    _description = "Mirakl Payment Gateway"

    active = fields.Boolean(string="Active GateWay", default=True)

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string="Code", required=True)

    multi_ecommerce_connector_id = fields.Many2one('setu.multi.ecommerce.connector',
                                                   string='Multi e-Commerce Connector', copy=False, required=True)

    def find_and_create_mirakl_payment_gateway(self, multi_ecommerce_connector_id, mirakl_payment_dict):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method is used to create the payment gateway if it not there in the odoo
        """
        payment_gateway_mkl_code=mirakl_payment_dict.get('payment_type') or "no_payment_gateway_mirakl"
        setu_mirakl_payment_gateway_id = self.search([('code', '=',payment_gateway_mkl_code), ('multi_ecommerce_connector_id', '=', multi_ecommerce_connector_id.id)], limit=1)
        if not setu_mirakl_payment_gateway_id:
            setu_mirakl_payment_gateway_id = self.create({'name': payment_gateway_mkl_code, 'code': payment_gateway_mkl_code, 'multi_ecommerce_connector_id': multi_ecommerce_connector_id.id})
        return setu_mirakl_payment_gateway_id