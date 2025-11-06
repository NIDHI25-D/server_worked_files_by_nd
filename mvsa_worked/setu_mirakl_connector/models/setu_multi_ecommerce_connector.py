# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging
_logger = logging.getLogger(__name__)

class SetuMultiEcommerceConnector(models.Model):
    _inherit = 'setu.multi.ecommerce.connector'

    def _get_number_of_multi_connector_count_mirakl(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: count the number of sale order and account move for particular record.
        """
        for record_id in self:
            record_id.mirakl_sale_order_count = len(record_id.mirakl_sale_order_ids)
            record_id.mirakl_account_move_count = len(record_id.account_move_ids)

    @api.model
    def _get_set_mirakl_order_status(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: set the default status as the first status from Mirakl Order Status.
        """
        mirakl_order_status_ids = self.env['setu.mirakl.order.status'].search([])
        if mirakl_order_status_ids:
            return [(6, 0, [mirakl_order_status_ids[0].id])]
        else:
            return False

    def _get_set_mirakl_order_from(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: set the default date of Import Mirakl Order From as last sale order's date if exists of particular those connector else set the date before 30 days from today.
        """
        sale_order_obj = self.env["sale.order"]
        order_after_date = datetime.now() - timedelta(30)
        if not self.import_mirakl_order_from:
            order_id = sale_order_obj.search([('multi_ecommerce_connector_id', '=', self.id)], order='date_order asc',
                                             limit=1) or False
            if order_id:
                order_after_date = order_id.date_order
            else:
                order_after_date = datetime.now() - timedelta(30)
            self.write({"import_mirakl_order_from": order_after_date})
        return order_after_date


    ecommerce_connector = fields.Selection(selection_add=[('mirakl_connector', 'Mirakl')],
                                           default='mirakl_connector', string="e-Commerce Connector",
                                           ondelete={'mirakl_connector': 'set default'})
    mirakl_host = fields.Char(string="Mirakl Host", required=True)
    mirakl_api_key = fields.Char(string="API Key", required=True)
    user_id = fields.Many2one('res.users', string='Salesperson')
    partner_invoice_id = fields.Many2one(comodel_name='res.partner',string="Invoice Address")
    mirakl_mapped_with_odoo_product = fields.Selection(
        [('default_code', 'Internal Reference(Default Code)')], string="Product Search Pattern",
        default='default_code')
    mirakl_order_status_ids = fields.Many2many('setu.mirakl.order.status',
                                                'setu_mirakl_ecommerce_connector_order_status_rel',
                                                'multi_ecommerce_connector_id', 'mirakl_order_status_id',
                                                "Mirakl Order Status", default=_get_set_mirakl_order_status)
    import_mirakl_order_from = fields.Datetime(string="Import Mirakl Order From", default=_get_set_mirakl_order_from)
    mirakl_payment_gateway_ids = fields.One2many('setu.mirakl.payment.gateway', 'multi_ecommerce_connector_id',
                                                  string="Mirakl Payment Gateway")
    mirakl_sale_order_ids = fields.One2many('sale.order', 'multi_ecommerce_connector_id', string="Mirakl Sale Orders")
    mirakl_sale_order_count = fields.Integer(compute='_get_number_of_multi_connector_count_mirakl',
                                              string="Mirakl Sale Order Count")
    account_move_ids = fields.One2many('account.move', 'multi_ecommerce_connector_id',
                                       string="Mirakl Customer Invoices")
    mirakl_account_move_count = fields.Integer(compute='_get_number_of_multi_connector_count_mirakl',
                                                string="Mirakl Customer Invoice")


    _sql_constraints = [('unique_host', 'unique(mirakl_host)',
                         "e-Commerce already exists for given host. Host must be Unique for the Mirakl e-Commerce!")]

    def cron_configuration_action(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: add new action if the connector is mirakl else worked as it is. 
        """
        if self.ecommerce_connector != 'mirakl_connector':
            return super().cron_configuration_action()
        else:
            action = self.env.ref('setu_mirakl_connector.setu_mirakl_cron_configuration_wiz_action').sudo().read()[0]
            action['context'] = {'multi_ecommerce_connector_id': self.id}
            return action

    def connection_mirakl_connector(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method is called when the Test connection from Mirakl connector is executed.
        """
        headers = {
            'Authorization': self.mirakl_api_key,
            'Content-Type': 'application/json',
        }
        url = f"{self.mirakl_host}/api/orders"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.text
                _logger.info(
                    f"Connector: {self.name} State is changed from--> {self.state} with Status code:{response.status_code}, Connector Type: {self.ecommerce_connector}")
                return {
                        'status': 'success',
                        'data':data
                    }
            else:
                _logger.info(
                    f"Connector: {self.name} State is changed from--> {self.state} with Status code:{response.status_code}, Connector Type: {self.ecommerce_connector}")
                return {
                    'status': 'error',
                    'code': response.status_code,
                    'message': response.text,
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

    def mirakl_connector_fully_integrate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: To fully integrate the connection.
        """
        if not (
                self.odoo_company_id or self.odoo_warehouse_id or self.mirakl_order_status_ids):
            raise ValidationError(_('Please select a company'))
        self.state = 'fully_integrated'
        _logger.info(f"State is changed to --> {self.state} for Connector:{self.name}, Connector Type: {self.ecommerce_connector}")
        return True

    def action_sale_order_count_mirakl(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method is used to count the sale order represent in the Kanban view
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_mirakl_connector.setu_multi_ecommerce_connector_sale_action_mirakl")
        return action

    def action_account_move_account_mirakl(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: This method is used to count the Invoice represent in the Kanban view
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_mirakl_connector.setu_mirakl_account_move_commerce_invoice_action")
        return action
