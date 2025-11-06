from odoo import api, fields, models
import datetime
from odoo.addons.website.models import ir_http
from io import BytesIO
import xlsxwriter
import base64
FONT_TITLE_LEFT = {'bold': True, 'align': 'left', 'font_color': 'red', 'bg_color': '#fff2cc'}
import logging
_logger = logging.getLogger("create_monthly_proposal_for_customers")
INSERT_BATCH_SIZE = 60
batch_size = 50
from odoo.tools.misc import split_every


class ResPartner(models.Model):
    _inherit = 'res.partner'

    monthly_proposal_pricelist_id = fields.Many2one('product.pricelist', string="Monthly Proposal Pricelist")
    date_to_create_sale_order = fields.Date(string='sale order create date',
                                            help="To identify the customer for "
                                                 "whom sale order is created on current date")
    watchdog_report_datas = fields.Binary('Content')

    def create_monthly_proposal(self, customer_ids=[]):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 28/04/25
            Task: 18 Migration
            Purpose: create monthly sale order based on previous month and current month sale order of previous year
                     if there is already a sale order of current month this year with same quantity then it will not create sale order.

            note: with_delay() used to create queue job , with with_delay() method execute when queue job triggered
        """
        if self.env['ir.module.module'].sudo().search([('name', '=', 'queue_job'), ('state', '=', 'installed')],
                                                      limit=1):
            self.monthly_proposal_create_and_update_sale_order(customer_ids)
            self.with_delay(description="res_partner.monthly_proposal_send_mail").monthly_proposal_send_mail()
            # self.monthly_proposal_send_mail()

    def monthly_proposal_create_and_update_sale_order(self,customer_ids):
        customers = self.browse(customer_ids).filtered(lambda cu: cu.monthly_proposal_pricelist_id.id
                                                                  and not cu.is_customer_locked) if customer_ids \
            else self.search([('monthly_proposal_pricelist_id', '!=', False),('is_customer_locked','=',False)])
        website = self.env['website'].search([], limit=1)
        query = ''
        if len(customers) > 1:
            query = """
                                   select customer,product,total_qty,pre_order,pre_sale from (select customer,product,sum(total_qty) as total_qty,pre_order,pre_sale from (with instock as (WITH RECURSIVE c AS (
                                                          SELECT id, location_id, id as tmp
                                                               from public.stock_location
                                                          UNION ALL
                                                          SELECT c.id, sa.location_id, c.location_id as tmp
                                                          FROM public.stock_location AS sa
                                                             JOIN c ON c.location_id = sa.id
                                                   )
                                                   select
                                                       ofd.product_id,
                                                       sum(quantity) as on_hand,
                                                       sum(quantity - outgoing_qty) as instock
                                                       From(
                                                           select
                                                              pp.id as product_id,
                                                              0 as quantity,
                                                              0 as outgoing_qty
                                                           from
                                                           public.product_product pp
                                                           inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           where pp.active = 't' and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)

                                                           union all

                                                           SELECT
                                                              sm.product_id,
                                                              0 as quantity,
                                                              sum("sm"."product_qty") AS "outgoing_qty"
                                                           FROM public."stock_move" as sm
                                                             LEFT JOIN public."stock_location" AS sml ON (sm.location_id = sml.id)
                                                             LEFT JOIN public."stock_location" AS "smld" ON (sm.location_dest_id = smld.id)
                                                             right join public.product_product pp on pp.id = sm.product_id
                                                             inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           WHERE sm."state" in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                                              AND sml.usage = 'internal' AND smld.usage != 'internal' AND pt.active = 't' and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)
                                                           GROUP BY sm.product_id

                                                           union all

                                                           SELECT
                                                             sq.product_id,
                                                             sum(sq.quantity) AS "quantity",
                                                             0 as outgoing_qty
                                                           from public.stock_quant sq
                                                               left join public.stock_location sl on sq.location_id = sl.id
                                                                   join c on c.id = sl.id
                                                                   join public.stock_warehouse sw on sw.view_location_id = c.tmp-- (select tmp from c where c.id = sl.id)
                                                                   right join public.product_product pp on pp.id = sq.product_id
                                                                   inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           where  sl.usage='internal' and pt.type != 'service'
                                                               and pp.active = 't' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)
                                                           GROUP BY sq.product_id
                                                       )ofd

                                                       group by ofd.product_id) ,
                                    all_information as( select customer,product,total_qty,coalesce(is_preorder,False) as is_preorder ,coalesce(is_presale,False) as is_presale from 
                                                     (WITH prev_month_data AS (
                                                     SELECT so.partner_id AS customer, sol.product_id AS product, sum(sol.qty_invoiced) AS qty , pp.available_for_preorder as is_preorder , pp.available_for_presale as is_presale
                                                     FROM sale_order_line sol
                                                     JOIN sale_order so ON sol.order_id = so.id
                                                     LEFT JOIN product_product pp ON sol.product_id = pp.id
                                                     inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                     WHERE so.date_order >= (select date_trunc('month', current_timestamp - interval '1' month) at time zone 'utc') AND so.date_order <= (select date_trunc('month', current_timestamp)at time zone 'utc')
                                                                 and sol.product_id is not null and sol.qty_invoiced > 0 and so.state in ('sale','done') and pt.type != 'service' 
                                                                 and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null) --and (pp.available_for_preorder != 't' and pp.available_for_presale != 't')--and so.partner_id =2227
                                                     GROUP BY so.partner_id, sol.product_id , pp.available_for_preorder , pp.available_for_presale
                                                   ), prev_year_data AS (
                                                     SELECT so.partner_id AS customer, sol.product_id AS product, sum(sol.qty_invoiced) AS qty, pp.available_for_preorder as is_preorder , pp.available_for_presale as is_presale
                                                     FROM sale_order_line sol
                                                     JOIN sale_order so ON sol.order_id = so.id
                                                     LEFT JOIN product_product pp ON sol.product_id = pp.id
                                                     inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                     WHERE so.date_order >= (select date_trunc('month', current_timestamp - interval '1' month) at time zone 'utc') - interval '1 year' AND so.date_order <= (select (date_trunc('month', current_timestamp) + interval '1 month') at time zone 'utc') - interval '1 year'
                                                                 and sol.product_id is not null and  sol.qty_invoiced > 0 and so.state in ('sale','done') and pt.type != 'service' 
                                                                 and  pt.is_published='t'
                                                                 And (pt.discontinued = 'f' or pt.discontinued is null) --and (pp.available_for_preorder != 't' and pp.available_for_presale != 't') --and so.partner_id =2227
                                                     GROUP BY so.partner_id, sol.product_id , pp.available_for_preorder , pp.available_for_presale
                                                   )

                                                   SELECT case when prev_month_data.customer is null then prev_year_data.customer else prev_month_data.customer end as customer ,
                                                          case when prev_month_data.product is null then prev_year_data.product else prev_month_data.product end as product, 
                                                          case when prev_month_data.qty is null then prev_year_data.qty else prev_year_data.qty - prev_month_data.qty end as total_qty,
                                                          case when prev_month_data.product is null then prev_year_data.is_preorder else prev_month_data.is_preorder end as is_preorder,
                                                          case when prev_month_data.product is null then prev_year_data.is_presale else prev_month_data.is_presale end as is_presale
                                                   FROM prev_year_data
                                                    left JOIN prev_month_data ON prev_month_data.customer = prev_year_data.customer AND prev_month_data.product = prev_year_data.product
                                                    )total_data where total_data.total_qty > 0)

                                   select  case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.customer
                                           else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                           else all_info.customer end end as customer,

                                           case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.product
                                           else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                           else all_info.product end end as product,

                                           case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.total_qty 
                                           else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                           else all_info.total_qty end end as total_qty,

                                           all_info.is_preorder as pre_order,
                                           all_info.is_presale as pre_sale

                                   from    all_information all_info 
                                   left join instock ins ON all_info.product = ins.product_id)final_data group by customer,product,pre_order,pre_sale)final_data_with_preorder_presale where final_data_with_preorder_presale.total_qty > 0 and final_data_with_preorder_presale.customer in {0};""".format(
                tuple(customers.ids) if len(customers) > 1 else customers.id or 'null')
        else:
            query = """
                               select customer,product,total_qty,pre_order,pre_sale from (select customer,product,sum(total_qty) as total_qty,pre_order,pre_sale from (with instock as (WITH RECURSIVE c AS (
                                                          SELECT id, location_id, id as tmp
                                                               from public.stock_location
                                                          UNION ALL
                                                          SELECT c.id, sa.location_id, c.location_id as tmp
                                                          FROM public.stock_location AS sa
                                                             JOIN c ON c.location_id = sa.id
                                                   )
                                                   select
                                                       ofd.product_id,
                                                       sum(quantity) as on_hand,
                                                       sum(quantity - outgoing_qty) as instock
                                                       From(
                                                           select
                                                              pp.id as product_id,
                                                              0 as quantity,
                                                              0 as outgoing_qty
                                                           from
                                                           public.product_product pp
                                                           inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           where pp.active = 't' and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)

                                                           union all

                                                           SELECT
                                                              sm.product_id,
                                                              0 as quantity,
                                                              sum("sm"."product_qty") AS "outgoing_qty"
                                                           FROM public."stock_move" as sm
                                                             LEFT JOIN public."stock_location" AS sml ON (sm.location_id = sml.id)
                                                             LEFT JOIN public."stock_location" AS "smld" ON (sm.location_dest_id = smld.id)
                                                             right join public.product_product pp on pp.id = sm.product_id
                                                             inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           WHERE sm."state" in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                                              AND sml.usage = 'internal' AND smld.usage != 'internal' AND pp.active = 't' and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)
                                                           GROUP BY sm.product_id

                                                           union all

                                                           SELECT
                                                             sq.product_id,
                                                             sum(sq.quantity) AS "quantity",
                                                             0 as outgoing_qty
                                                           from public.stock_quant sq
                                                               left join public.stock_location sl on sq.location_id = sl.id
                                                                   join c on c.id = sl.id
                                                                   join public.stock_warehouse sw on sw.view_location_id = c.tmp-- (select tmp from c where c.id = sl.id)
                                                                   right join public.product_product pp on pp.id = sq.product_id
                                                                   inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                           where  sl.usage='internal'
                                                               and pp.active = 't' and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null)
                                                           GROUP BY sq.product_id
                                                       )ofd

                                                       group by ofd.product_id) ,
                                all_information as( select customer,product,total_qty,coalesce(is_preorder,False) as is_preorder ,coalesce(is_presale,False) as is_presale from 
                                                 (WITH prev_month_data AS (
                                                 SELECT so.partner_id AS customer, sol.product_id AS product, sum(sol.qty_invoiced) AS qty , pp.available_for_preorder as is_preorder , pp.available_for_presale as is_presale
                                                 FROM sale_order_line sol
                                                 JOIN sale_order so ON sol.order_id = so.id
                                                 LEFT JOIN product_product pp ON sol.product_id = pp.id
                                                 inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                 WHERE so.date_order >= (select date_trunc('month', current_timestamp - interval '1' month) at time zone 'utc') AND so.date_order <= (select date_trunc('month', current_timestamp)at time zone 'utc')
                                                             and sol.product_id is not null and sol.qty_invoiced > 0 and so.state in ('sale','done') 
                                                             and  pt.is_published='t'
                                                             and pt.type != 'service' And (pt.discontinued = 'f' or pt.discontinued is null) --and (pp.available_for_preorder != 't' and pp.available_for_presale != 't')--and so.partner_id =2227
                                                 GROUP BY so.partner_id, sol.product_id , pp.available_for_preorder , pp.available_for_presale
                                               ), prev_year_data AS (
                                                 SELECT so.partner_id AS customer, sol.product_id AS product, sum(sol.qty_invoiced) AS qty, pp.available_for_preorder as is_preorder , pp.available_for_presale as is_presale
                                                 FROM sale_order_line sol
                                                 JOIN sale_order so ON sol.order_id = so.id
                                                 LEFT JOIN product_product pp ON sol.product_id = pp.id
                                                 inner join public.product_template pt on pt.id = pp.product_tmpl_id
                                                 WHERE so.date_order >= (select date_trunc('month', current_timestamp - interval '1' month) at time zone 'utc') - interval '1 year' AND so.date_order <= (select (date_trunc('month', current_timestamp) + interval '1 month') at time zone 'utc') - interval '1 year'
                                                             and sol.product_id is not null and  sol.qty_invoiced > 0 and so.state in ('sale','done') 
                                                             and pt.type != 'service' and pt.is_published='t' And (pt.discontinued = 'f' or pt.discontinued is null) --and (pp.available_for_preorder != 't' and pp.available_for_presale != 't') --and so.partner_id =2227
                                                 GROUP BY so.partner_id, sol.product_id , pp.available_for_preorder , pp.available_for_presale
                                               )

                                               SELECT case when prev_month_data.customer is null then prev_year_data.customer else prev_month_data.customer end as customer ,
                                                      case when prev_month_data.product is null then prev_year_data.product else prev_month_data.product end as product, 
                                                      case when prev_month_data.qty is null then prev_year_data.qty else prev_year_data.qty - prev_month_data.qty end as total_qty,
                                                      case when prev_month_data.product is null then prev_year_data.is_preorder else prev_month_data.is_preorder end as is_preorder,
                                                      case when prev_month_data.product is null then prev_year_data.is_presale else prev_month_data.is_presale end as is_presale
                                               FROM prev_year_data
                                                left JOIN prev_month_data ON prev_month_data.customer = prev_year_data.customer AND prev_month_data.product = prev_year_data.product
                                                )total_data where total_data.total_qty > 0)

                               select  case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.customer
                                       else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                       else all_info.customer end end as customer,

                                       case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.product
                                       else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                       else all_info.product end end as product,

                                       case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock > 0  then all_info.total_qty 
                                       else case when (all_info.is_preorder = 't' or all_info.is_presale = 't') and ins.instock <= 0 then null 
                                       else all_info.total_qty end end as total_qty,

                                       all_info.is_preorder as pre_order,
                                       all_info.is_presale as pre_sale

                               from    all_information all_info 
                               left join instock ins ON all_info.product = ins.product_id)final_data group by customer,product,pre_order,pre_sale)final_data_with_preorder_presale where final_data_with_preorder_presale.total_qty > 0 and final_data_with_preorder_presale.customer = {0};""".format(
                tuple(customers.ids) if len(customers) > 1 else customers.id or 'null')
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        total_customer = False
        cutomers_list_to_create_or_update_order = list(map(lambda y: y['customer'], data))
        customers = customers.filtered(lambda cus:cus.id in cutomers_list_to_create_or_update_order) if customers else False


        if customers:
            for batch in split_every(batch_size, customers.ids):
                batch_data = list(filter(lambda p: p["customer"] in list(batch), data))
                self.with_delay(description="res_partner.monthly_create_update_sale_order").monthly_create_update_sale_order(monthly_customer_ids=list(batch), interval_customer_ids=False,
                                                      data=batch_data)
                # self.monthly_create_update_sale_order(monthly_customer_ids=list(batch), interval_customer_ids=False,
                #                                       data=batch_data)



    def monthly_proposal_send_mail(self):
        domain = [('is_monthly_proposal', '=', True), ('state', '=', 'draft')]
        template_id = self.env.ref('setu_monthly_sale_order_proposal.mail_template_to_notify_user_for_proposal')
        sale_order_ids = self.env['sale.order'].search(domain)
        created_sale_order_ids = sale_order_ids.filtered(lambda x: x.create_date.date() == datetime.date.today())
        updated_sale_order_ids = sale_order_ids.filtered(lambda x: x.write_date.date() == datetime.date.today() and x.create_date.date() != datetime.date.today())
        website = self.env['website'].search([], limit=1)
        # template_id = self.env.ref('setu_monthly_sale_order_proposal.mail_template_to_notify_user_for_proposal')
        file_data = self.create_excel_report(created_sale_order_ids=created_sale_order_ids,
                                             updated_sale_order_ids=updated_sale_order_ids)
        attachment = self.env['ir.attachment'].create({
            'name': f'MonthlyProposalReport.xlsx',
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'datas': file_data,
        })

        mail = self.env['ir.default'].sudo()._get('res.config.settings', 'monthly_proposal_mail_user',company_id=self.env.company.id)
        if mail and template_id:
            try:
                user_id = self.env['res.users'].browse(int(mail))
                template_id.send_mail(self.env.user.id, force_send=True,
                                      email_values={'recipient_ids': [user_id.partner_id.id],
                                                    'email_from': website.company_id.email,
                                                    'attachment_ids': [attachment.id]})
                _logger.info(f"mail sent to all customer.")
            except Exception as e:
                _logger.info(f"Issue in mail configuration.")

    def get_order_line_values(self, customer, data):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 29/04/25
            Task: 18 Migration
            Purpose: prepare sale order line vals
        """
        line_vals = []
        line_vals.extend({'product_id': i.get('product'), 'product_uom_qty': i.get('total_qty')} for i in data if
                         i.get('customer') == customer.id)
        values_to_write = [(0, 0, p) for p in line_vals]
        return values_to_write

    def _compute_last_website_so_id(self):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 30/04/25
            Task: 18 Migration
            Purpose: compute last website sale order when cart load
        """
        super()._compute_last_website_so_id()
        SaleOrder = self.env['sale.order']
        for partner in self:
            is_public = partner.is_public
            website = ir_http.get_request_website()
            if website and not is_public:
                if partner.monthly_proposal_pricelist_id:
                    last_monthly_proposal_order = SaleOrder.search([
                        ('partner_id', '=', partner.id),
                        ('pricelist_id', '=', partner.monthly_proposal_pricelist_id.id),
                        ('website_id', '=', website.id),
                        ('state', '=', 'draft'),
                        ('is_preorder', '=', False),
                        ('is_presale', '=', False),
                        ('is_next_day_shipping', '=', False),
                        ('is_international_preorder', '=', False),
                        ('is_monthly_interval_proposal', '=', True),
                        ('is_monthly_proposal', '=', True)
                    ], order='write_date desc', limit=1)
                    monthly_proposal_order = SaleOrder.search([
                        ('partner_id', '=', partner.id),
                        ('pricelist_id', '=', partner.monthly_proposal_pricelist_id.id),
                        ('website_id', '=', website.id),
                        ('state', '=', 'draft'),
                        ('is_preorder', '=', False),
                        ('is_presale', '=', False)
                    ], order='write_date desc', limit=1)
                    if last_monthly_proposal_order:
                        partner.last_website_so_id = last_monthly_proposal_order
                    elif monthly_proposal_order:
                        partner.last_website_so_id = monthly_proposal_order
                if not partner.last_website_so_id:
                    partner.last_website_so_id = SaleOrder.search([
                        ('partner_id', '=', partner.id),
                        ('pricelist_id', 'in', partner.allowed_pricelists.ids),
                        ('website_id', '=', website.id),
                        ('state', '=', 'draft'),
                    ], order='write_date desc', limit=1)

    def create_interval_proposal(self):
        if self.env['ir.module.module'].sudo().search([('name', '=', 'queue_job'), ('state', '=', 'installed')],
                                                      limit=1):
            self.monthly_interval_proposal_create_and_update_sale_order()
            self.with_delay(description="res_partner.monthly_interval_proposal_send_mail").monthly_interval_proposal_send_mail()
            # self.monthly_interval_proposal_send_mail()

    def monthly_create_update_sale_order(self, monthly_customer_ids, interval_customer_ids, data):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 30/04/25
            Task: 18 Migration
            Purpose: create or update sale order
            args:= monthly_customer_ids:  customers if monthly proposal
                interval_customer_ids: customers if interal proposal
                data: data (dict) from query result
        """
        partner_env = self.env['res.partner']
        website = self.env['website'].search([], limit=1)
        customer_ids = False
        template_id = False
        if monthly_customer_ids:
            # customer_ids = monthly_customer_ids
            customer_ids = partner_env.browse(monthly_customer_ids)
            template_id = self.env.ref(
                    'setu_monthly_sale_order_proposal.mail_template_to_notify_customer_for_proposal')
        elif interval_customer_ids:
            # customer_ids = interval_customer_ids
            customer_ids = partner_env.browse(interval_customer_ids)
            template_id = self.env.ref(
                    'setu_monthly_sale_order_proposal.mail_template_to_notify_customer_for_interval_proposal')

        total_customer = len(customer_ids) if customer_ids else False
        mail_to_user_while_create_or_update_order = []
        mail_to_customers = []
        saleorder_obj = self.env['sale.order']
        if customer_ids :
            for index, cus in enumerate(
                    customer_ids.filtered(lambda date: date.date_to_create_sale_order != datetime.date.today()), start=1):
                cus_data = list(filter(lambda p: p["customer"] == cus.id, data))

                addr = cus.address_get(['delivery'])
                domain = [('partner_id', '=', cus.id), ('website_id', '=', website.id), ('state', '=', 'draft'),
                          ('is_preorder', '=', False), ('is_presale', '=', False)]

                if interval_customer_ids:
                    extra_domain = [('is_next_day_shipping', '=', False), ('is_international_preorder', '=', False)]
                    domain += extra_domain
                order = saleorder_obj.search(domain, order='write_date desc', limit=1)
                if order and order.is_monthly_proposal:
                    order.action_cancel()
                    order.unlink()
                    order = False
                elif order and order.is_monthly_interval_proposal:
                    order.action_cancel()
                    order.unlink()
                    order = False
                if not order:
                    # order_line_values = self.get_order_line_values(customer=cus, data=data)
                    order_line_values = self.get_order_line_values(customer=cus, data=cus_data)
                    if order_line_values:
                        values = {
                            'partner_id': cus.id,
                            'pricelist_id': cus.monthly_proposal_pricelist_id.id or self.env[
                                'product.pricelist'].search([('currency_id', '=', self.env.company.currency_id.id)],
                                                            limit=1).id,
                            # 'payment_term_id': website.sale_get_payment_term(cus),
                                # 'payment_term_id': website._compute_payment_term_id(),
                            # 'team_id': website.salesteam_id.id or cus.parent_id.team_id.id or cus.team_id.id,
                            'team_id': website.salesteam_id.id,
                            'partner_invoice_id': cus.id,
                            'partner_shipping_id': addr['delivery'],
                            'user_id': False,
                            'website_id': website.id,
                            'is_monthly_proposal': True if monthly_customer_ids or self._context.get('is_monthly_interval') else False,
                            'is_monthly_interval_proposal': True if interval_customer_ids else False,
                            'order_line': order_line_values,
                            'is_from_website': True
                            }
                        try:
                            # task:- Monthly propossals Issue {https://app.clickup.com/t/86dxxd7j7}
                            # modified:- add changes related to condition all user for check limit for monthly prposal.
                            ord = saleorder_obj.create(values)
                            user_id = self.env['res.users'].search([
                                ('partner_id', '=', cus.id)], limit=1)
                            if (user_id and not user_id.has_group('base.group_portal')) or not user_id:
                                check_limit = ord.with_context(from_monthly_cron=True).check_limit()
                                if not check_limit:
                                    ord.action_cancel()
                                    ord.unlink()
                                    order = False
                                    continue
                            ord._compute_warehouse_id()
                            ord.action_update_prices()
                            mail_to_customers.append(cus.id)
                            ord.partner_id.write({'date_to_create_sale_order': datetime.date.today()})
                            _logger.info(
                                f"Monthly proposal order '{ord.name}' is created for {cus.name}---{index}---out of---{total_customer}")
                        except Exception as e:
                            mail_to_user_while_create_or_update_order.append(
                                (cus.name, f"{e}", "while creating sale order"))
                            _logger.exception(f"Got the error '{e}' with customer {cus.name}")
                elif order:
                    # line_values_to_write = self.get_order_line_values(customer=cus, data=data)
                    line_values_to_write = self.get_order_line_values(customer=cus, data=cus_data)

                    if line_values_to_write:
                        try:
                            order.write({
                                'is_monthly_proposal': True if monthly_customer_ids or self._context.get('is_monthly_interval') else False,
                                'is_monthly_interval_proposal': True if interval_customer_ids else False,
                                'order_line': line_values_to_write})
                            user_id = self.env['res.users'].search([
                                ('partner_id', '=', cus.id)], limit=1)
                            if (user_id and not user_id.has_group('base.group_portal')) or not user_id:
                                check_limit = order.with_context(from_monthly_cron=True).check_limit()
                                if not check_limit:
                                    order.action_cancel()
                                    order.unlink()
                                    order = False
                                    continue
                            order._compute_warehouse_id()
                            if cus.monthly_proposal_pricelist_id:
                                order.pricelist_id = cus.monthly_proposal_pricelist_id.id
                            order.action_update_prices()
                            order.is_monthly_proposal = True if monthly_customer_ids else False
                            order.is_monthly_interval_proposal = True if interval_customer_ids else False
                            mail_to_customers.append(cus.id)
                            order.partner_id.write({'date_to_create_sale_order': datetime.date.today()})
                            _logger.info(
                                f"Monthly interval proposal order '{order.name}' is written for {cus.name}---{index}---out of---{total_customer}")
                        except Exception as e:
                            mail_to_user_while_create_or_update_order.append(
                                (cus.name, f"{e}", "while updating sale order"))
                            _logger.exception(f"Got the error '{e}' with customer {cus.name}")

        if not customer_ids:
            for data in split_every(INSERT_BATCH_SIZE, mail_to_customers):
                try:
                    if data and template_id:
                        template_id.send_mail(self.env.user.id,
                                              email_values={'recipient_ids': list(data),
                                                            'email_from': website.company_id.email})
                        _logger.info(f"Mail sent to all customer.")
                except Exception as e:
                    _logger.info(f"Issue in mail configuration.")
        else:
            try:
                if customer_ids and template_id:
                    template_id.send_mail(self.env.user.id,
                                          email_values={'recipient_ids': customer_ids,
                                                        'email_from': website.company_id.email})
                    _logger.info(f"Mail sent to all customer.")
            except Exception as e:
                _logger.info(f"Issue in mail configuration.")
        return True

    def monthly_interval_proposal_create_and_update_sale_order(self):
        """
            Authour:sagar.pandya@setconsulting.com
            Date: 29/04/25
            Task: 18 Migration
            Purpose: 1)get data that met interval proposal condition
                    2) send data to create sale order for batchwise customers
        """
        query = """
            SELECT
              customer,
              product,
              total_qty,
              pre_order,
              pre_sale
            FROM
              (
                SELECT
                  customer,
                  product,
                  SUM(total_qty) AS total_qty,
                  pre_order,
                  pre_sale
                FROM
                  (
                    WITH
                      instock AS (
                        WITH RECURSIVE
                          c AS (
                            SELECT id, location_id, id AS tmp FROM public.stock_location
                            UNION ALL
                            SELECT c.id, sa.location_id, c.location_id AS tmp FROM public.stock_location AS sa
                              JOIN c ON c.location_id=sa.id
                          )
                        SELECT
                          ofd.product_id, SUM(quantity) AS on_hand, SUM(quantity-outgoing_qty) AS instock
                        FROM
                          (
                            SELECT
                              pp.id AS product_id, 0 AS quantity, 0 AS outgoing_qty
                            FROM
                              public.product_product pp
                              INNER JOIN public.product_template pt ON pt.id=pp.product_tmpl_id
                            WHERE
                              pp.active='t'
                              AND pt.type!='service'
                              AND pt.is_published='t'
                            UNION ALL
                            SELECT
                              sm.product_id,
                              0 AS quantity,
                              SUM("sm"."product_qty") AS "outgoing_qty"
                            FROM
                              public."stock_move" AS sm
                              LEFT JOIN public."stock_location" AS sml ON (sm.location_id=sml.id)
                              LEFT JOIN public."stock_location" AS "smld" ON (sm.location_dest_id=smld.id)
                              RIGHT JOIN public.product_product pp ON pp.id=sm.product_id
                              INNER JOIN public.product_template pt ON pt.id=pp.product_tmpl_id
                            WHERE
                              sm."state" IN (
                                'waiting',
                                'confirmed',
                                'assigned',
                                'partially_available'
                              )
                              AND sml.usage='internal'
                              AND smld.usage!='internal'
                              AND pt.active='t'
                              AND pt.type!='service'
                              AND pt.is_published='t'
                            GROUP BY
                              sm.product_id
                            UNION ALL
                            SELECT
                              sq.product_id,
                              SUM(sq.quantity) AS "quantity",
                              0 AS outgoing_qty
                            FROM
                              public.stock_quant sq
                              LEFT JOIN public.stock_location sl ON sq.location_id=sl.id
                              JOIN c ON c.id=sl.id
                              JOIN public.stock_warehouse sw ON sw.view_location_id=c.tmp -- (select tmp from c where c.id = sl.id)
                              RIGHT JOIN public.product_product pp ON pp.id=sq.product_id
                              INNER JOIN public.product_template pt ON pt.id=pp.product_tmpl_id
                            WHERE
                              sl.usage='internal'
                              AND pt.type!='service'
                              AND pp.active='t'
                              AND pt.is_published='t'
                            GROUP BY
                              sq.product_id
                          ) ofd
                        GROUP BY
                          ofd.product_id
                      ),
                      all_information AS (
                        SELECT
                          customer,
                          product,
                          total_qty,
                          COALESCE(is_preorder, FALSE) AS is_preorder,
                          COALESCE(is_presale, FALSE) AS is_presale,
                          COALESCE(next_day_shipping, FALSE) AS next_day_shipping,
                          COALESCE(is_international_pre_order_product, FALSE) AS is_international_pre_order_product
                        FROM
                          (
                            WITH
                              prev_month_data AS (
                                SELECT
                                  so.partner_id AS customer,
                                  sol.product_id AS product,
                                  SUM(sol.qty_invoiced) AS qty,
                                  pp.available_for_preorder AS is_preorder,
                                  pp.available_for_presale AS is_presale,
                                  pt.next_day_shipping AS next_day_shipping,
                                  pp.is_international_pre_order_product AS is_international_pre_order_product
                                FROM
                                  sale_order_line sol
                                  JOIN sale_order so ON sol.order_id=so.id
                                  LEFT JOIN product_product pp ON sol.product_id=pp.id
                                  INNER JOIN public.product_template pt ON pt.id=pp.product_tmpl_id
                                WHERE
                                  so.date_order>=(
                                    SELECT
                                      date_trunc ('month', CURRENT_TIMESTAMP-INTERVAL '1 month') AT TIME zone 'utc'
                                  )
                                  AND so.date_order<=(
                                    SELECT
                                      date_trunc ('month', CURRENT_TIMESTAMP) AT TIME zone 'utc'
                                  )
                                  AND sol.product_id IS NOT NULL
                                  AND sol.qty_invoiced>0
                                  AND so.state IN ('sale', 'done')
                                  AND pt.type!='service'
                                  AND pt.is_published='t'
                                GROUP BY
                                  so.partner_id,
                                  sol.product_id,
                                  pp.available_for_preorder,
                                  pp.available_for_presale,
                                  pt.next_day_shipping,
                                  pp.is_international_pre_order_product
                              ),
                              prev_year_data AS (
                                SELECT
                                  so.partner_id AS customer,
                                  sol.product_id AS product,
                                  SUM(sol.qty_invoiced) AS qty,
                                  pp.available_for_preorder AS is_preorder,
                                  pp.available_for_presale AS is_presale,
                                  pt.next_day_shipping AS next_day_shipping,
                                  pp.is_international_pre_order_product AS is_international_pre_order_product
                                FROM
                                  sale_order_line sol
                                  JOIN sale_order so ON sol.order_id=so.id
                                  LEFT JOIN product_product pp ON sol.product_id=pp.id
                                  INNER JOIN public.product_template pt ON pt.id=pp.product_tmpl_id
                                  LEFT JOIN public.res_partner rp ON rp.id=so.partner_id
                                WHERE
                                  so.date_order<=(
                                    SELECT
                                      (
                                        date_trunc ('month', CURRENT_TIMESTAMP)-INTERVAL '1 month'
                                      ) AT TIME zone 'utc'
                                  )
                                  AND sol.product_id IS NOT NULL
                                  AND sol.qty_invoiced>0
                                  AND so.state IN ('sale', 'done')
                                  AND pt.type!='service'
                                  AND pt.is_published='t'
                                GROUP BY
                                  so.partner_id,
                                  sol.product_id,
                                  pp.available_for_preorder,
                                  pp.available_for_presale,
                                  pt.next_day_shipping,
                                  pp.is_international_pre_order_product
                              )
                            SELECT
                              CASE WHEN prev_month_data.customer IS NULL THEN prev_year_data.customer
                                ELSE prev_month_data.customer
                              END AS customer,
                              CASE WHEN prev_month_data.product IS NULL THEN prev_year_data.product
                                ELSE prev_month_data.product
                              END AS product,
                              CASE WHEN prev_month_data.qty IS NULL THEN prev_year_data.qty
                                ELSE prev_year_data.qty-prev_month_data.qty
                              END AS total_qty,
                              CASE WHEN prev_month_data.product IS NULL THEN prev_year_data.is_preorder
                                ELSE prev_month_data.is_preorder
                              END AS is_preorder,
                              CASE WHEN prev_month_data.product IS NULL THEN prev_year_data.is_presale
                                ELSE prev_month_data.is_presale
                              END AS is_presale,
                              CASE WHEN prev_month_data.product IS NULL THEN prev_year_data.next_day_shipping
                                ELSE prev_month_data.next_day_shipping
                              END AS next_day_shipping,
                              CASE WHEN prev_month_data.product IS NULL THEN prev_year_data.is_international_pre_order_product
                                ELSE prev_month_data.is_international_pre_order_product
                              END AS is_international_pre_order_product
                            FROM prev_year_data
                              LEFT JOIN prev_month_data ON prev_month_data.customer=prev_year_data.customer
                              AND prev_month_data.product=prev_year_data.product
                          ) total_data
                        WHERE total_data.total_qty>0
                      )
                    SELECT
                      CASE WHEN (
                          all_info.is_preorder='t'
                          OR all_info.is_presale='t'
                          OR all_info.next_day_shipping='t'
                          OR all_info.is_international_pre_order_product='t'
                        )
                        AND ins.instock<=0 THEN NULL
                        ELSE all_info.customer
                      END AS customer,
                      CASE WHEN (
                          all_info.is_preorder='t'
                          OR all_info.is_presale='t'
                          OR all_info.next_day_shipping='t'
                          OR all_info.is_international_pre_order_product='t'
                        )
                        AND ins.instock<=0 THEN NULL
                        ELSE all_info.product
                      END AS product,
                      CASE WHEN (
                          all_info.is_preorder='t'
                          OR all_info.is_presale='t'
                          OR all_info.next_day_shipping='t'
                          OR all_info.is_international_pre_order_product='t'
                        )
                        AND ins.instock<=0 THEN NULL
                        ELSE all_info.total_qty
                      END AS total_qty,
                      all_info.is_preorder AS pre_order,
                      all_info.is_presale AS pre_sale,
                      all_info.next_day_shipping AS next_day_shipping,
                      all_info.is_international_pre_order_product AS is_international_pre_order_product
                    FROM all_information all_info
                      LEFT JOIN instock ins ON all_info.product=ins.product_id
                  ) final_data GROUP BY customer, product, pre_order, pre_sale
              ) final_data_with_preorder_presale WHERE final_data_with_preorder_presale.total_qty > 0
                  AND final_data_with_preorder_presale.customer IN (
                    SELECT rp.id FROM res_partner rp WHERE rp.monthly_proposal_pricelist_id IS NOT NULL
                      AND age (CURRENT_DATE, rp.create_date)>=INTERVAL '3 MONTHS'
                      AND age (CURRENT_DATE, rp.create_date)<=INTERVAL '1 YEAR + 1 DAY'
              );
        """

        customers = self.env['res.partner'].search([('monthly_proposal_pricelist_id', '!=', False),
                                                    ('date_to_create_sale_order', '!=', datetime.date.today())])
        self._cr.execute(query)
        data = self._cr.dictfetchall()
        customers_list_to_create_or_update_order = list(map(lambda y: y['customer'], data))
        customers = customers.filtered(lambda cus: cus.id in customers_list_to_create_or_update_order)

        if customers:
            for batch in split_every(batch_size, customers.ids):
                batch_data = list(filter(lambda p: p["customer"] in list(batch), data))
                self.with_context(is_monthly_interval=True).with_delay(description="res_partner.monthly_create_update_sale_order").monthly_create_update_sale_order(monthly_customer_ids=False,
                                                                                             interval_customer_ids=list(batch),
                                                                                             data=batch_data)
                # self.with_context(is_monthly_interval=True).monthly_create_update_sale_order(monthly_customer_ids=False,
                                                                                             # interval_customer_ids=list(batch),
                                                                                             # data=batch_data)



    def monthly_interval_proposal_send_mail(self):
        """
              Authour:sagar.pandya@setconsulting.com
              Date: 29/04/25
              Task: 18 Migration
              Purpose: send mail with attachment
        """
        domain = [('is_monthly_interval_proposal', '=', True), ('state', '=', 'draft')]
        template_id = self.env.ref(
            'setu_monthly_sale_order_proposal.mail_template_to_notify_user_for_interval_proposal')
        sale_order_ids = self.env['sale.order'].search(domain)
        created_sale_order_ids = sale_order_ids.filtered(lambda x: x.create_date.date() == datetime.date.today())
        updated_sale_order_ids = sale_order_ids.filtered(
            lambda x: x.write_date.date() == datetime.date.today() and x.create_date.date() != datetime.date.today())
        website = self.env['website'].search([], limit=1)
        file_data = self.create_excel_report(created_sale_order_ids=created_sale_order_ids,
                                             updated_sale_order_ids=updated_sale_order_ids)
        attachment = self.env['ir.attachment'].create({
            'name': f'MonthlyIntervalProposalReport.xlsx',
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'datas': file_data,
        })

        mail = self.env['ir.default'].sudo()._get('res.config.settings', 'monthly_proposal_mail_user',
                                                 company_id=self.env.company.id)
        if mail and template_id:
            try:
                user_id = self.env['res.users'].browse(int(mail))
                template_id.send_mail(self.env.user.id, force_send=True,
                                      email_values={'recipient_ids': [user_id.partner_id.id],
                                                    'email_from': website.company_id.email,
                                                    'attachment_ids': [attachment.id]})
                _logger.info(f"mail sent to all customer.")
            except Exception as e:
                _logger.info(f"Issue in mail configuration.")

    def create_excel_report(self, created_sale_order_ids, updated_sale_order_ids):
        """
              Authour:sagar.pandya@setconsulting.com
              Date: 29/04/25
              Task: 18 Migration
              Purpose: create attachment
        """
        data = BytesIO()
        workbook = xlsxwriter.Workbook(data)
        wb_new_format = workbook.add_format(FONT_TITLE_LEFT)
        if created_sale_order_ids:
            worksheet1 = workbook.add_worksheet("Sale order created")
            worksheet1.set_column(0, 0, 50)
            worksheet1.set_column(0, 1, 30)
            worksheet1.write(0, 0, "customer name", wb_new_format)
            worksheet1.write(0, 1, 'sale order name', wb_new_format)
            for row_index, line in enumerate(created_sale_order_ids, start=1):
                worksheet1.write(row_index, 0, line.partner_id.name)
                worksheet1.write(row_index, 1, line.name)
        if updated_sale_order_ids:
            worksheet2 = workbook.add_worksheet("Sale order updated")
            worksheet2.set_column(0, 0, 50)
            worksheet2.set_column(0, 1, 30)
            worksheet2.write(0, 0, "customer name", wb_new_format)
            worksheet2.write(0, 1, "sale order name", wb_new_format)
            for row_index, line in enumerate(updated_sale_order_ids, start=1):
                worksheet2.write(row_index, 0, line.partner_id.name)
                worksheet2.write(row_index, 1, line.name)
        workbook.close()

        data.seek(0)
        file_data = base64.encodebytes(data.read())
        self.write({'watchdog_report_datas': file_data})
        data.close()
        return file_data
