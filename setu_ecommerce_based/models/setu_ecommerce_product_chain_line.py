# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SetuEcommerceProductChainLine(models.Model):
    _name = 'setu.ecommerce.product.chain.line'
    _description = 'eCommerce Product Chain Line'

    # Char and Text fields
    name = fields.Char(string="Product", translate=True)
    ecommerce_product_id = fields.Char(string="Product Chain", translate=True)
    last_product_chain_update_date = fields.Char(string='Last Product Chain', translate=True)
    product_chain_line_data = fields.Text(string="Product Chain Line Data")

    # Datetime fields
    last_product_chain_line_process_date = fields.Datetime(string="Last Process Date")

    state = fields.Selection(
        selection=[("draft", "Draft"), ("fail", "Fail"),
                   ("done", "Done"), ("cancel", "Cancelled")],
        default="draft", string="State")

    # Relational fields
    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string='Multi e-Commerce Connector', copy=False)
    setu_ecommerce_product_chain_id = fields.Many2one(
        comodel_name="setu.ecommerce.product.chain",
        required=True, ondelete="cascade", copy=False)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_confirmed(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will check if product chain line done you cannot remove
        :return: None
        """
        if self._check_process_line():
            raise ValidationError(_('You can not remove processed chain line'))

    def _check_process_line(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : Filtered done order chain line
        :return: product chain line records
        """
        return self.filtered(lambda process_line_id: process_line_id.state == 'done')

    @api.model
    def cron_auto_import_ecommerce_product_chain_line(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to auto process for product chain line based cron configuration
        :return: True
        """
        multi_ecommerce_connector_ids = self.search([('state', '=', 'draft')]).mapped('multi_ecommerce_connector_id')
        for multi_ecommerce_connector_id in multi_ecommerce_connector_ids:
            if hasattr(self,
                       '%s_auto_process_ecommerce_product_chain_line' % multi_ecommerce_connector_id.ecommerce_connector):
                getattr(self,
                        '%s_auto_process_ecommerce_product_chain_line' % multi_ecommerce_connector_id.ecommerce_connector)()
        return True

    def initialize_ecommerce_process_product_chain_line(self, product_chain_ids):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to initialize process order chain line
        :param product_chain_ids:
        :return: True
        """
        for product_chain_id in product_chain_ids:
            product_chain_id.no_records_processed += 1
            if product_chain_id.no_records_processed > 4:
                product_chain_id.is_action_require = True
                note = (
                    _("<p>The schedule action of e-Commerce: Process Product Queue is running on background and current"
                      " record should be time executed for more than given period. Need to process Queue manually</p>"))
                product_chain_id.message_post(body=note)
                continue
            product_chain_line_ids = product_chain_id.setu_ecommerce_product_chain_line_ids
            product_chain_line_ids.ecommerce_process_product_chain_line()
        return True

    def ecommerce_process_product_chain_line(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to process for order chain line
        :return: True
        """
        if hasattr(self, '%s_process_product_chain_line' % self.multi_ecommerce_connector_id.ecommerce_connector):
            getattr(self, '%s_process_product_chain_line' % self.multi_ecommerce_connector_id.ecommerce_connector)()
        return True
