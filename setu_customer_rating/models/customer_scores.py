# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _
import logging
_logger = logging.getLogger(__name__)
glob_customers = []


class CustomerScore(models.Model):
    _name = "customer.score"
    _rec_name = 'partner_id'
    _description = "Customer Score"

    # Integer and Float Fields
    partner_score = fields.Integer(string="Score")
    avg_monthly_sales_score = fields.Integer(
        string="Average Monthly Sales",
        help="(Sales amount - refund amount)/months)")
    avg_monthly_refund_score = fields.Integer(
        string="Average monthly sales refunds",
        help="(Refund amount * 100 /Sales amount)")
    qty_invoice_paid_score = fields.Integer(
        string="Quantity of Invoices paid after the due date",
        help="Number of invoices paid after the due date (including grace days)")
    amount_invoice_paid_score = fields.Integer(
        string="Amount of Invoices paid after the due date",
        help="Amount of invoices paid after due date (including grace days)")
    qty_invoices_due_after_60_days_score = fields.Integer(
        string="Quantity of invoices due after X days",
        help="Number of overdue invoices outstanding")
    amount_invoices_due_after_60_days_score = fields.Integer(
        string="Amount of invoices due after X days",
        help="The outstanding amount of overdue invoices")
    average_payment_days_score = fields.Integer(
        string="Average payment days in your purchase history",
        help="Average days in paying")
    pre_sale_orders_canceled_score = fields.Integer(string="Percentage of pre-sale orders canceled")
    total_score = fields.Integer(string="Total Score")
    average_monthly_amount = fields.Float(string="Average amount", default=0.0)
    sales_average_for_refund_percentage = fields.Float(string="Sales average", default=0.0)
    refund_average_for_refund_percentage = fields.Float(string="Refund average", default=0.0)
    due_qty = fields.Integer(string="Due qty", default=0)
    due_date_amount = fields.Float(string="Due date amount", default=0.0)
    due_after_60_quantity = fields.Integer(string="Quantity", default=0)
    due_after_60_amount = fields.Float(string="Amount", default=0.0)
    avg_pay_days = fields.Integer(string="Days", default=0)
    average_amount_sales_average = fields.Float(string="Sales Amount", default=0.0)
    average_amount_refund_average = fields.Float(string="Refund Amount", default=0.0)

    # Relational Fields
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer")
    partner_rating = fields.Many2one(comodel_name="customer.rating", string="Rating")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    sale_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="average_sale_rel",
        column1="score_id",
        column2="sale_id",
        string="Sales")
    pos_order_ids = fields.Many2many(
        comodel_name="pos.order",
        relation="average_pos_sale_rel",
        column1="score_id",
        column2="pos_order_id",
        string="POS Orders")
    canceled_pre_orders = fields.Many2many(
        comodel_name="sale.order",
        relation="customer_score_canceled_sales_rel",
        column1="score_id",
        column2="sale_id",
        string="Canceled Pre Orders")
    invoice_done_after_due_date_ids = fields.Many2many(
        comodel_name="account.move",
        relation="customer_score_paid_after_due_invoice_rel",
        column1="score_id",
        column2="invoice_id",
        string="Done Invoice After Due Date")
    invoices_due_after_60_days = fields.Many2many(
        comodel_name="account.move",
        relation="customer_score_unpaid_after_60_days_invoice_rel",
        column1="score_id",
        column2="invoice_id",
        string="Invoices Due After 60 Days")
    credit_notes = fields.Many2many(
        comodel_name="account.move",
        relation="customer_score_refund_invoice_rel",
        column1="score_id",
        column2="invoice_id",
        string="Credit Notes")
    invoices = fields.Many2many(
        comodel_name="account.move",
        relation="customer_score_invoice_rel",
        column1="score_id",
        column2="invoice_id",
        string="Invoices")

    customer_rating_history = fields.One2many(
        comodel_name="setu.partner.rating.history",
        inverse_name="customer_score_id",
        string="Rating History")

    def run_customer_score_cron(self):
        """
            task : https://app.clickup.com/t/86dx5vmq9 { customer rating }
                dispatch partner batches to job queue instead of processing directly.
        """
        partner_ids = self.env['res.partner'].search([('customer_rank', '>', 0)]).ids
        batch_size = 500
        _logger.info(f"Dispatching jobs for {len(partner_ids)} partners")

        for i in range(0, len(partner_ids), batch_size):
            batch = partner_ids[i:i + batch_size]
            self.with_delay()._process_customer_score_batch(batch)
            # self._process_customer_score_batch(batch)
        _logger.info("All customer score jobs dispatched to queue.")

    def _process_customer_score_batch(self,partner_ids):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 03/01/2025
        Task: [1393] Setu Customer Rating v18
        Purpose: This method is used to create customer score, set score and update customer rating
        :return: None
        """
        self._cr.execute("select * from create_customer_score_records(%s::int[])", (partner_ids,))
        _logger.info("Completion of function : create_customer_score_records()")
        days = int(self.env['ir.config_parameter'].sudo().get_param(
            f'setu_customer_rating.customer_score_days_{self.env.company.id}')) or 365
        invoice_days = int(self.env['ir.config_parameter'].sudo().get_param(
            f'setu_customer_rating.past_days_for_invoice_{self.env.company.id}')) or 60
        grace_days_to_paid_invoice = int(self.env['ir.config_parameter'].sudo().get_param(
            f'setu_customer_rating.grace_days_to_paid_invoice_{self.env.company.id}')) or 0
        invoice_due_date_limit = str(date.today() - relativedelta(days=invoice_days))
        date_limit = str(date.today() - relativedelta(days=days))
        months = int(days / 30)

        score_conf_avg_sales_amt_id = self.env.ref('setu_customer_rating.score_conf_avg_sales_amt').id
        score_conf_avg_monthly_sales_refund_id = self.env.ref(
            'setu_customer_rating.score_conf_avg_monthly_sales_refund').id
        score_conf_qty_invoice_paid_after_due_id = self.env.ref(
            'setu_customer_rating.score_conf_qty_invoice_paid_after_due').id
        score_conf_amt_invoice_paid_after_due_id = self.env.ref(
            'setu_customer_rating.score_conf_amt_invoice_paid_after_due').id
        score_conf_qty_invoice_paid_after_x_days_id = self.env.ref(
            'setu_customer_rating.score_conf_qty_invoice_paid_after_x_days').id
        score_conf_amt_invoices_due_after_x_days_id = self.env.ref(
            'setu_customer_rating.score_conf_amt_invoices_due_after_x_days').id
        score_conf_avg_payment_days_id = self.env.ref('setu_customer_rating.score_conf_avg_payment_days').id
        partner_ids_sql = "ARRAY[%s]" % ",".join(map(str, partner_ids))
        self._cr.execute(
            f"""Select * from set_customer_scores('{date_limit}',{months if months > 0 else 1},
                                                    '{invoice_due_date_limit}',
                                                    {grace_days_to_paid_invoice},
                                                    {score_conf_avg_sales_amt_id},
                                                    {score_conf_avg_monthly_sales_refund_id},
                                                    {score_conf_qty_invoice_paid_after_due_id},
                                                    {score_conf_amt_invoice_paid_after_due_id},
                                                    {score_conf_qty_invoice_paid_after_x_days_id},
                                                    {score_conf_amt_invoices_due_after_x_days_id},
                                                    {score_conf_avg_payment_days_id},{partner_ids_sql})""",
                                                    )
        _logger.info("Completion of function :set_customer_scores ()")
        self._cr.execute(
            f"select * from set_document_ids('{date_limit}','{invoice_due_date_limit}',{grace_days_to_paid_invoice},{partner_ids_sql})")
        _logger.info("Completion of function : set_document_ids()")
        self._cr.execute("select * from update_rating_data(%s)", (partner_ids,))
        _logger.info("Completion of function : update_rating_data()")
        self.run_customer_rating_history_cron(partner_ids)
        _logger.info("Completion of function : run_customer_rating_history_cron()")

    def run_customer_rating_history_cron(self,partner_ids):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 03/01/2025
        Task: [1393] Setu Customer Rating v18
        Purpose: This method is used to create customer score, set score and update customer rating
        :return: None
        """
        manage_history_query = """ with crt as (    
                                        Select 
                                            rp.id as partner_id,
                                            company_value::integer AS company_id,
	                                        rating_value::integer AS current_rating,
                                            (select	now() :: timestamp without time zone) as date_changed
                                        FROM res_partner rp,
                                        LATERAL jsonb_each_text(rp.rating::jsonb) AS json_data(company_value, rating_value)
                                         WHERE rp.id = ANY(%s)
                                    ),
                                    total_score as (
                                        Select 
                                            rp.id as partner_id,
                                    	    company_value::integer AS company_id,
	                                        total_score_value::integer AS current_total_score
                                        FROM res_partner rp,
                                        LATERAL jsonb_each_text(rp.total_score::jsonb) AS json_data(company_value, total_score_value)
                                        WHERE rp.id = ANY(%s)
                                    ),
                                    previous_detail as (
                                      Select
                                        ROW_NUMBER () OVER (
                                          partition by partner_id
                                          ORDER BY
                                            date_changed desc
                                        ) rank,
                                        partner_id as partner_id,
                                        current_customer_rating_id as previous_customer_rating_id,
                                        current_total_score as previous_total_score
                                      from
                                        setu_partner_rating_history
                                        WHERE partner_id = ANY(%s)
                                    ),
									c_rating as (select id from customer_rating where from_score = 0)
									
                                    Insert into setu_partner_rating_history(
                                      partner_id, company_id, current_customer_rating_id,
                                      previous_customer_rating_id,
                                       current_total_score,
                                       previous_total_score,date_changed)
                                    select
                                      total_score.partner_id as partner_id,
                                      total_score.company_id as company_id,
                                      crt.current_rating as current_customer_rating_id,
                                      case when previous_customer_rating_id is not null then previous_customer_rating_id else (select * from c_rating) end as previous_customer_rating_id,
                                      coalesce(current_total_score,0) as current_total_score,
                                      coalesce(previous_total_score,0) as previous_total_score,
                                      crt.date_changed as date_changed
                                    from
                                      crt
                                      join total_score on total_score.partner_id = crt.partner_id
                                      full outer join previous_detail on total_score.partner_id = previous_detail.partner_id and rank = 1
                                    where
                                      crt.current_rating is not null 
									  and total_score.current_total_score != coalesce(previous_detail.previous_total_score, 0);"""

        self._cr.execute(manage_history_query,(partner_ids, partner_ids, partner_ids))
        self._cr.execute("""UPDATE setu_partner_rating_history historys 
                        set customer_score_id = cs.id
                        FROM   customer_score  cs
                        where historys.customer_score_id is null and 
                        cs.partner_id = historys.partner_id
                         AND historys.partner_id = ANY(%s);""",(partner_ids,))

    def avg_monthly_sales_score_for_customer(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Average Sales Amount
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_avg_sales_amt').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def avg_monthly_refund_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Average Monthly Sales Refund
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_avg_monthly_sales_refund').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def amount_invoice_paid_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Amount Of Invoices Paid After Due Date
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_amt_invoice_paid_after_due').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def qty_invoice_paid_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Quantity Of invoices Paid After Due Date
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_qty_invoice_paid_after_due').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def amount_invoices_due_after_60_days_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Amount Of Invoices Due After X Days
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_amt_invoices_due_after_x_days').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def qty_invoices_due_after_60_days_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Quantity of Invoices Due after X Days
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_qty_invoice_paid_after_x_days').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }

    def average_payment_days_score_for_customer(self):
        """
            Author: Siddharth@setuconsulting.com
            Date: 25/08/23
            Task: Customer rating improvement.
            Purpose: to redirect at Average Payment Days in Purchase History
        """
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'score.conf',
            'res_id': self.env.ref('setu_customer_rating.score_conf_avg_payment_days').id,
            'target': 'new',
            'context': {'create': False, 'edit': False},
        }
