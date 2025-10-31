 # -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, api


class SetuEcommerceProductChain(models.Model):
    _name = "setu.ecommerce.product.chain"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "eCommerce Product Chain"

    # Conditional fields
    is_skip_existing_product_update = fields.Boolean(string="Do Not Update Existing Products")
    is_chain_in_process = fields.Boolean(string="Is Chain Processing", default=False)
    is_action_require = fields.Boolean(default=False)

    # Char fields
    name = fields.Char(translate=True)
    current_status = fields.Char(default="Running...", translate=True)

    # Selection fields
    state = fields.Selection(
        selection=[("draft", "Draft"), ("in_progress", "In Progress"), ("fail", "Fail"),
                   ("completed", "Completed"), ('cancel', 'Cancel')],
        default="draft", compute="_compute_chain_state", store=True, tracking=True)
    record_created_from = fields.Selection(
        selection=[("import_process", "Via Import Process"),
                   ("webhook", "Via Webhook")],
        string="Record Created From")

    # Integer fields
    no_records_processed = fields.Integer(string="No Records Processed")
    total_product_records = fields.Integer(
        string="Total Records",
        compute="_get_total_count_product_records")
    total_draft_product_records = fields.Integer(
        string="Draft Records",
        compute="_get_total_count_product_records")
    total_fail_product_records = fields.Integer(
        string="Fail Records",
        compute="_get_total_count_product_records")
    total_done_product_records = fields.Integer(
        string="Done Records",
        compute="_get_total_count_product_records")
    total_cancel_product_records = fields.Integer(
        string="Cancelled Records",
        compute="_get_total_count_product_records")

    # Relational fields
    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector", copy=False)
    ecommerce_connector = fields.Selection(
        string="e-Commerce Connector",
        related="multi_ecommerce_connector_id.ecommerce_connector", store=True)
    process_history_id = fields.Many2one(
        comodel_name="setu.process.history",
        string="Process History")
    process_history_line_ids = fields.One2many(
        related="process_history_id.process_history_line_ids")
    setu_ecommerce_product_chain_line_ids = fields.One2many(
        comodel_name="setu.ecommerce.product.chain.line",
        inverse_name="setu_ecommerce_product_chain_id",
        string="Product Chain Line")

    @api.depends("setu_ecommerce_product_chain_line_ids.state")
    def _get_total_count_product_records(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to compute product chain state like total draft, done, fail, cancel product
        :return: None
        """
        for product_chain_id in self:
            total_line_ids = product_chain_id.setu_ecommerce_product_chain_line_ids
            product_chain_id.total_product_records = len(total_line_ids)
            product_chain_id.total_draft_product_records = len(
                total_line_ids.filtered(lambda line_id: line_id.state == "draft"))
            product_chain_id.total_fail_product_records = len(
                total_line_ids.filtered(lambda line_id: line_id.state == "fail"))
            product_chain_id.total_done_product_records = len(
                total_line_ids.filtered(lambda line_id: line_id.state == "done"))
            product_chain_id.total_cancel_product_records = len(
                total_line_ids.filtered(lambda line_id: line_id.state == "cancel"))

    @api.depends("setu_ecommerce_product_chain_line_ids.state")
    def _compute_chain_state(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to compute product chain state
        :return: None
        """
        for product_chain_id in self:
            if product_chain_id.total_product_records == product_chain_id.total_done_product_records + product_chain_id.total_cancel_product_records:
                product_chain_id.state = "completed"
            elif product_chain_id.total_draft_product_records == product_chain_id.total_product_records:
                product_chain_id.state = "draft"
            elif product_chain_id.total_product_records == product_chain_id.total_fail_product_records:
                product_chain_id.state = "fail"
            else:
                product_chain_id.state = "in_progress"

    @api.model_create_multi
    def create(self, vals_list):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to generate sequence for product chain record
        :param vals_list:
        :return: product chain recordset
        """
        for vals in vals_list:
            seq = self.env["ir.sequence"].next_by_code("setu.ecommerce.product.chain") or "/"
            vals.update({"name": seq or ""})
        return super(SetuEcommerceProductChain, self).create(vals_list)

    def ecommerce_process_create_product_chain(self, multi_ecommerce_connector_id, record_created_from,
                                               is_skip_existing_product):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to create product chain
        :param multi_ecommerce_connector_id:
        :param record_created_from:
        :param is_skip_existing_product:
        :return:
        """
        return self.create(
            {"multi_ecommerce_connector_id": multi_ecommerce_connector_id and multi_ecommerce_connector_id.id or False,
             "record_created_from": record_created_from,
             'is_skip_existing_product_update': is_skip_existing_product})

    def ecommerce_process_create_product_chain_line_vals(self, multi_ecommerce_connector_id, ecommerce_product_chain):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to prepare order chain line
        :param multi_ecommerce_connector_id:
        :param ecommerce_product_chain:
        :return:
        """
        return {
            'multi_ecommerce_connector_id': multi_ecommerce_connector_id and multi_ecommerce_connector_id.id,
            'last_product_chain_line_process_date': datetime.now(),
            'setu_ecommerce_product_chain_id': ecommerce_product_chain and ecommerce_product_chain.id}
