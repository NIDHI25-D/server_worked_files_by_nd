from odoo import api, fields, models, _
from odoo.tools import config
import subprocess
from odoo import registry, SUPERUSER_ID, api
import logging
import threading
from datetime import datetime,timedelta
_logger = logging.getLogger("postgres")


class setuRefreshMaterializedView(models.Model):
    _name = 'setu.refresh.materialized.view'
    _description = 'Refresh Materialized View'

    def cron_refresh_materialized_view(self):
        _logger.info(f"start refresh materialized cron")
        db_host = config.get('db_host') or '127.0.0.1'
        database_name = self.env.cr.dbname
        db_registry = registry(database_name)

        if self.env['ir.module.module'].sudo().search([('name', '=', 'queue_job'), ('state', '=', 'installed')],
                                                      limit=1):
            # self.with_delay().refresh_materialized_view_recruit_atte_emp_invoice(db_host, database_name)
            self.with_delay().refresh_materialized_view_journal_prodstock_vendor_purchaseline(db_host, database_name)
            self.with_delay().refresh_materialized_view_saleline_trasnfer_invoiceline(db_host, database_name)
            self.with_delay().refresh_materialized_view_transferline_prodinfo(db_host, database_name)
            self.with_delay().refresh_materialized_view_sale_contact_purchase(db_host, database_name)

    def cron_check_pending_stage_of_que_job(self):
        interval_minutes = self.env['ir.config_parameter'].sudo().get_param('setu_product_view_by_vendor.interval_time_to_send_mail')
        user_id = eval(self.env['ir.config_parameter'].sudo().get_param('setu_product_view_by_vendor.mail_to'))
        model_id = self.env['ir.model'].search([('model', '=', 'setu.refresh.materialized.view')])
        if user_id and interval_minutes:
            user_id = self.env['res.users'].browse(user_id)
            email_to = ','.join(user.partner_id.email for user in user_id if user.partner_id)
            queue_job_ids = self.env['queue.job'].search(
                [('state', '=', 'pending'), ('job_function_id.model_id', '=', model_id.id)])
            failed_queue_job_ids = self.env['queue.job'].search(
                [('state', '=', 'failed'), ('job_function_id.model_id', '=', model_id.id),
                 ('delete_mail_at_once', '=', False)])
            queue_job_after_interval = queue_job_ids.filtered(
                lambda date: date.date_created + timedelta(minutes=interval_minutes) < datetime.now())

            if user_id and email_to and (queue_job_after_interval or failed_queue_job_ids):
                if failed_queue_job_ids:
                    failed_queue_job_ids.delete_mail_at_once = True
                mail_values = {
                    'email_from': self.env.company.email,
                    'email_to': email_to,
                    'body_html': f"There are queuejobs in pending or failed stage",
                    'subject': 'Pending Quejobs',
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()

    def refresh_materialized_view_journal_prodstock_vendor_purchaseline(self, db_host, database_name):
        password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
        queue_job_uuid = self.env.context.get('job_uuid')
        queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])
        _logger.info("start_refresh_view_get_journal_items_view")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.get_journal_items_view';",
            shell=True)
        _logger.info("end_refresh_get_journal_items_view")

        _logger.info("start_refresh_view_get_product_template_stock_info_materialized_view")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.get_product_template_stock_info_materialized_view';",
            shell=True)
        _logger.info("end_refresh_get_product_template_stock_info_materialized_view")

        _logger.info("start_refresh_view materialized_view_of_product_by_vendor")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_product_by_vendor';",
            shell=True)
        _logger.info("end_refresh_materialized_view_of_product_by_vendor")

        body = _(
            "Following views refreshed \n (1) 'journal_item_view' \n (2) 'product_stock_info_view' \n (3) 'product_view_by_view' \n ")

        subject = _("Refresh view")

        queue_job_id.message_post(body=body, subject=subject)

    def refresh_materialized_view_saleline_trasnfer_invoiceline(self, db_host, database_name):
        password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
        queue_job_uuid = self.env.context.get('job_uuid')
        queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])

        _logger.info("start_refresh_view_materialized_view_of_sale_order_line")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_sale_order_line';",
            shell=True)
        _logger.info("end_refresh_materialized_view_of_sale_order_line")

        _logger.info("start_refresh_materialized_view_of_sale_order_line_invoice_rel")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_sale_order_line_invoice_rel';",
            shell=True)
        _logger.info("end_refresh_materialized_view_of_sale_order_line_invoice_rel")

        body = _(
            "Following views refreshed \n (1) 'sale_order_line_view' \n (2) 'sale_order_line_invoice_rel_view'\n ")

        subject = _("Refresh view")

        queue_job_id.message_post(body=body, subject=subject)

    def refresh_materialized_view_transferline_prodinfo(self, db_host, database_name):
        password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
        queue_job_uuid = self.env.context.get('job_uuid')
        queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])

        _logger.info("start_refresh_view_materialized_view_of_prod_tmp_basic_info_view")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_prod_tmp_basic_info_view';",
            shell=True)
        _logger.info("end_refresh_materialized_view_of_prod_tmp_basic_info_view")

        body = _(
            "Following views refreshed \n (1) 'product_info_view' \n ")

        subject = _("Refresh view")


        queue_job_id.message_post(body=body, subject=subject)

    def refresh_materialized_view_sale_contact_purchase(self, db_host, database_name):
        password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
        queue_job_uuid = self.env.context.get('job_uuid')
        queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])

        _logger.info("start_refresh_view_materialized_contact")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_contact_view';",
            shell=True)
        _logger.info("end_refresh_materialized_contact")

        _logger.info("start_refresh_view_materialized_view_of_sale_order")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_sale_order';",
            shell=True)
        _logger.info("end_refresh_materialized_view_of_sale_order")

        _logger.info("start_refresh_view fleet_service")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_fleet_service';",
            shell=True)
        _logger.info("end_refresh_fleet_service")

        body = _(
            "Following views refreshed \n (1) 'contact_view' \n (2) 'sale_order_view' \n (3) 'fleet_service_view' \n ")

        subject = _("Refresh view")

        queue_job_id.message_post(body=body, subject=subject)

    def cron_refresh_materialized_view_daily(self):
        _logger.info(f"start refresh materialized weekly cron")
        db_host = config.get('db_host') or '127.0.0.1'
        database_name = self.env.cr.dbname

        if self.env['ir.module.module'].sudo().search([('name', '=', 'queue_job'), ('state', '=', 'installed')],
                                                      limit=1):
            self.with_delay().refresh_materialized_view_daily(db_host, database_name)

    def refresh_materialized_view_daily(self, db_host, database_name):
        password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
        queue_job_uuid = self.env.context.get('job_uuid')
        queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])

        _logger.info("start_refresh_view_materialized_view_of_journal_entries")
        subprocess.call(
            f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.materialized_view_of_journal_entries';",
            shell=True)
        _logger.info("end_materialized_view_of_journal_entries")

        body = _(
            "Following views refreshed \n (1) 'Journal Entries'")

        subject = _("Refresh view")

        queue_job_id.message_post(body=body, subject=subject)

    # def refresh_materialized_view_recruit_atte_emp_invoice(self, db_host, database_name):
    #     password_odoo14_datastudio = "MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj"
    #     queue_job_uuid = self.env.context.get('job_uuid')
    #     queue_job_id = self.env['queue.job'].search([('uuid', '=', queue_job_uuid)])
    #
    #     _logger.info("start_refresh_get_recruitments_view")
    #     subprocess.call(
    #         f"PGPASSWORD='{password_odoo14_datastudio}' psql -h {db_host} -U {'odoo14_datastudio'} -d {database_name} -c 'REFRESH MATERIALIZED VIEW datastudio_reports.get_recruitments_view';",
    #         shell=True)
    #     _logger.info("end_refresh_get_recruitments_view")
    #
    #     body = _(
    #         "Following views refreshed \n (1) 'recruitment_view' \n (2) 'attendance_view' \n (3) 'employee_view' \n (4) 'customer_invoice_view' \n (5) 'stock_quant' \n (6) 'hr_applicant_view' \n (7) 'hr_job_view' \n (8) 'credit_notes_view' \n  (9) 'journal_items_analytic_distribution_view' \n (10) 'mail_activity' \n (11) 'customers_invoice_payments' \n (11) 'transport_delivery_order' \n (12) 'materialized_view_of_shipping'")
    #
    #
    #     subject = _("Refresh view")
    #
    #     queue_job_id.message_post(body=body, subject=subject)
