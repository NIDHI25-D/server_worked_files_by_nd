# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SetuEcommerceOrderChain(models.Model):
    _name = "setu.ecommerce.order.chain"
    _description = "eCommerce Order Chain"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Conditional fields
    is_chain_in_process = fields.Boolean(string="Is Chain Processing", default=False)
    is_action_require = fields.Boolean(string="Action Require", default=False)

    # Char fields
    current_status = fields.Char(default="Running...", translate=True)
    name = fields.Char(string="Name", readonly=True, translate=True)

    # Selection fields
    record_created_from = fields.Selection(
        selection=[("import_process", "Via Import Process"), ("webhook", "Via Webhook"),
                   ("scheduled_action", "Via Scheduled Action")],
        default="import_process")
    state = fields.Selection(
        selection=[("draft", "Draft"), ("in_progress", "In Progress"),
                   ("completed", "Completed"), ("fail", "fail")],
        tracking=True, default="draft", copy=False,
        compute="_compute_order_state", store=True)

    # Integer compute fields
    total_orders_records = fields.Integer(
        string="Total Records",
        compute="_get_total_count_orders_records")
    total_draft_order_records = fields.Integer(
        string="Draft Records",
        compute="_get_total_count_orders_records")
    total_fail_order_records = fields.Integer(
        string='Fail Records',
        compute='_get_total_count_orders_records')
    total_done_order_records = fields.Integer(
        string="Done Records",
        compute="_get_total_count_orders_records")
    total_cancel_order_records = fields.Integer(
        string="Cancel Records",
        compute="_get_total_count_orders_records")
    no_records_processed = fields.Integer(string="No Records Processed")

    # Relational fields
    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector")
    ecommerce_connector = fields.Selection(
        related="multi_ecommerce_connector_id.ecommerce_connector",
        string="e-Commerce Connector", store=True)
    process_history_id = fields.Many2one(
        comodel_name="setu.process.history",
        string="Process History")
    process_history_line_ids = fields.One2many(
        related="process_history_id.process_history_line_ids",
        string="Process History Line")
    setu_ecommerce_order_chain_line_ids = fields.One2many(
        comodel_name="setu.ecommerce.order.chain.line",
        inverse_name="setu_ecommerce_order_chain_id", string="Order Chain Line")

    @api.depends('setu_ecommerce_order_chain_line_ids.state')
    def _compute_order_state(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to compute order chain state
        :return: None
        """
        for order_chain_id in self:
            if order_chain_id.total_orders_records == order_chain_id.total_done_order_records + order_chain_id.total_cancel_order_records:
                order_chain_id.state = "completed"
            elif order_chain_id.total_draft_order_records == order_chain_id.total_orders_records:
                order_chain_id.state = "draft"
            elif order_chain_id.total_orders_records == order_chain_id.total_fail_order_records:
                order_chain_id.state = "fail"
            else:
                order_chain_id.state = "in_progress"

    @api.depends('setu_ecommerce_order_chain_line_ids.state')
    def _get_total_count_orders_records(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to compute order chain state like total draft, done, fail, cancel order
        :return: None
        """
        for order_chain_id in self:
            order_chain_line_ids = order_chain_id.setu_ecommerce_order_chain_line_ids
            order_chain_id.total_orders_records = len(order_chain_line_ids)
            order_chain_id.total_draft_order_records = len(
                order_chain_line_ids.filtered(lambda chain_id: chain_id.state == "draft"))
            order_chain_id.total_done_order_records = len(
                order_chain_line_ids.filtered(lambda chain_id: chain_id.state == "done"))
            order_chain_id.total_fail_order_records = len(
                order_chain_line_ids.filtered(lambda chain_id: chain_id.state == "fail"))
            order_chain_id.total_cancel_order_records = len(
                order_chain_line_ids.filtered(lambda chain_id: chain_id.state == "cancel"))

    @api.model_create_multi
    def create(self, vals_list):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to generate sequence for order chain record
        :param vals_list:
        :return: order chain recordset
        """
        for vals in vals_list:
            seq = self.env["ir.sequence"].next_by_code("setu.ecommerce.order.chain") or "/"
            vals.update({"name": seq or ""})
        return super(SetuEcommerceOrderChain, self).create(vals_list)

    def ecommerce_process_create_order_chain(self, multi_ecommerce_connector_id, orders_data, record_created_from):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to create order chain
        :param multi_ecommerce_connector_id:
        :param orders_data:
        :param record_created_from:
        :return: order chain recordset
        """
        while orders_data:
            vals = {"multi_ecommerce_connector_id": multi_ecommerce_connector_id.id,
                    "record_created_from": record_created_from}
            order_data = orders_data[:50]
            if order_data:
                order_chain_id = self.create(vals)
                order_chain_id.ecommerce_process_create_order_chain_line(order_data)
                del orders_data[:50]
            return order_chain_id

    def ecommerce_process_create_order_chain_line(self, order_data):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to create order chain line
        :param order_data:
        :return: order chain line or False
        """
        setu_ecommerce_order_chain_line_obj = self.env["setu.ecommerce.order.chain.line"]
        vals_list = []
        for order in order_data:
            vals_list.append(
                {"setu_ecommerce_order_chain_id": self.id,
                 "multi_ecommerce_connector_id": self.multi_ecommerce_connector_id and self.multi_ecommerce_connector_id.id,
                 "ecommerce_order_id": order["id"],
                 "order_chain_line_data": order, "name": order["number"]})
        if vals_list:
            return setu_ecommerce_order_chain_line_obj.create(vals_list)
        return False

    @api.model
    def cron_auto_import_ecommerce_order_chain(self, ctx={}):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : This method will use to auto create order chain based on cron configuration
        :param ctx:
        :return:
        """
        multi_ecommerce_connector_id = ctx.get('multi_ecommerce_connector_id')
        multi_ecommerce_connector_id = self.env['setu.multi.ecommerce.connector'].browse(multi_ecommerce_connector_id)
        if hasattr(self, '%s_import_ecommerce_order_chain' % multi_ecommerce_connector_id.ecommerce_connector):
            getattr(self, '%s_import_ecommerce_order_chain' % multi_ecommerce_connector_id.ecommerce_connector)(
                multi_ecommerce_connector_id)
        return True

    def action_redirect_order_process_history(self):
        """
        @name : Kamlesh Singh
        @date : 28/10/2024
        @purpose : View process history line when import order
        :return:
        """
        return {'name': _('Process History Line'),
                'view_mode': 'list',
                'res_model': 'setu.process.history.line',
                'view_id': self.env.ref('setu_ecommerce_based.setu_process_history_line_tree_view').id,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.process_history_line_ids.ids)]}
