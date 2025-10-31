from odoo import fields, http, SUPERUSER_ID, _
from odoo.addons.portal.controllers import portal
from odoo.http import request
import datetime
from dateutil.relativedelta import relativedelta


class CustomerPortal(portal.CustomerPortal):

    @http.route(['/my/statistics'], type='http', auth="user", website=True)
    def portal_my_charts(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method is called when the controller "my statistics " is executed.
                     Its seen in the website -> below my account.This method gathers all the product as per the
                     condition and then bifurcate as per the product_type_marvelsa in the table : Best Selling products in your area
        """
        top_products = """
            select * from (
            select
            trim((select regexp_replace(to_json(pt.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as prod_name,
            pt.id,pp.default_code,pt.product_type_marvelsa,sum(aml.quantity) as qty,ROW_NUMBER () OVER (PARTITION by pt.product_type_marvelsa order by sum(aml.quantity) desc ) rank
            from account_move_line aml
            INNER join account_move am on aml.move_id = am.id
            INNER JOIN product_product pp ON pp.id = aml.product_id
            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
            where am.partner_id in (select id from res_partner where zip = '{zip}')
            AND am.state = 'posted'
            and aml.display_type = 'product'
            AND aml.account_id IS NOT NULL
            AND am.move_type = 'out_invoice'
            AND am.invoice_date  >=  date_trunc('month', timezone('America/Mexico_City', now()))
            and pt.product_type_marvelsa is not null
            group by pt.product_type_marvelsa , pt.id ,pt.description,pp.default_code
            order by pt.product_type_marvelsa, qty desc
            )d where rank < 21 group by d.product_type_marvelsa,d.qty,d.rank,d.id,d.default_code,d.prod_name order by d.product_type_marvelsa,d.qty desc
        """.format(zip = request.env.user.partner_id.zip)
        request._cr.execute(top_products)
        top_products_data = request._cr.dictfetchall()
        values = {'top_prodcts':top_products_data}
        return request.render("setu_customer_statistics_on_portal.portal_my_charts",values)

    @http.route(['/my/charts/purchase_history'], type='json', auth="user", website=True, csrf=False)
    def purchase_history(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method gives the record for the mix chart: line and column which includes the data of :
                    current month previous year, current month and previous month with the conditions mentioned in the queries.
        """
        main_curr_table = request.env['res.currency']._get_simple_currency_table(request.env.companies)
        main_curr_table = request.env.cr.mogrify(main_curr_table).decode(request.env.cr.connection.encoding)
        current_month_query = """
        SELECT
            COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS cm_quantity,
            COALESCE(sum(-aml.balance * account_currency_table.rate),0) AS cm_amount_total_signed,
            TO_CHAR(timezone('America/Mexico_City', now()),'Mon YYYY')  AS cm_year
        FROM
            account_move_line aml
        LEFT JOIN
            account_move am ON am.id = aml.move_id
            LEFT JOIN product_product product ON product.id = aml.product_id
            LEFT JOIN product_template template ON template.id = product.product_tmpl_id
            LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
            LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
            JOIN {currency_table} ON account_currency_table.company_id = aml.company_id
        WHERE
            am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = {partner} or id = {partner})
            AND am.state = 'posted'
            AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            AND am.invoice_date  >=  date_trunc('month', timezone('America/Mexico_City', now()))
            AND aml.display_type = 'product'
            AND aml.account_id IS NOT NULL
            ;""".format(currency_table=main_curr_table,partner=request.env.user.partner_id.id)
        # JOIN {currency_table} ON currency_table.company_id = aml.company_id
        # request.env['account.move'].search([('payment_state','=','paid'),('move_type','=','out_invoice'),('partner_id','child_of',request.env.user.partner_id.id)])
        request._cr.execute(current_month_query)
        current_month_data = request._cr.dictfetchall()

        # Previous month
        previous_month_query = """
        SELECT
            COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS pm_quantity,
            COALESCE(sum(-aml.balance * account_currency_table.rate),0) AS pm_amount_total_signed,
            TO_CHAR(timezone('America/Mexico_City', now() - interval '1' month),'Mon YYYY') AS pm_year
        FROM
            account_move_line aml
        LEFT JOIN
            account_move am ON am.id = aml.move_id
            LEFT JOIN product_product product ON product.id = aml.product_id
            LEFT JOIN product_template template ON template.id = product.product_tmpl_id
            LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
            LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
            JOIN {currency_table} ON account_currency_table.company_id = aml.company_id
        WHERE
            am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = {partner} or id = {partner})
            AND am.state = 'posted'
            AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            AND am.invoice_date  <= date_trunc('month', timezone('America/Mexico_City', now()))
            AND am.invoice_date  >=  date_trunc('month', timezone('America/Mexico_City', now() - interval '1' month))
            AND aml.display_type = 'product'
            AND aml.account_id IS NOT NULL
        ;""".format(currency_table=main_curr_table,partner=request.env.user.partner_id.id)
        request._cr.execute(previous_month_query)
        previous_month_data = request._cr.dictfetchall()

        # Last Year Same Month
        last_year_same_month ="""
        SELECT
                     COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS lysm_quantity,
                     COALESCE(sum(-aml.balance * account_currency_table.rate),0) as  lysm_amount_total_signed,
                     TO_CHAR(timezone('America/Mexico_City', now() - interval '1' year),'Mon YYYY') AS lysm_year
                     FROM
                         account_move_line aml
                     LEFT JOIN
                         account_move am ON am.id = aml.move_id
                         LEFT JOIN product_product product ON product.id = aml.product_id
                         LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                         LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
                         LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                         JOIN {currency_table} ON account_currency_table.company_id = aml.company_id
                     
                     WHERE
                         am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = {partner} or id = {partner})
                         AND am.state = 'posted'
                         AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                         AND am.invoice_date  < date_trunc('month', timezone('America/Mexico_City', now() - interval '11' month))
	                    and am.invoice_date  >= date_trunc('month', timezone('America/Mexico_City', now() - interval '1' year))
                         AND aml.display_type = 'product'
                         AND aml.account_id IS NOT NULL
                     """.format(currency_table=main_curr_table,partner=request.env.user.partner_id.id)
        request._cr.execute(last_year_same_month)
        last_year_same_month_data = request._cr.dictfetchall()


        return {
                'price_data': [last_year_same_month_data[0]['lysm_amount_total_signed'],
                               current_month_data[0]['cm_amount_total_signed'],previous_month_data[0]['pm_amount_total_signed']
                               ],
                'unit_data': [last_year_same_month_data[0]['lysm_quantity'],
                              current_month_data[0]['cm_quantity'], previous_month_data[0]['pm_quantity']
                              ],
                'year_data': [last_year_same_month_data[0]['lysm_year'],
                              current_month_data[0]['cm_year'],previous_month_data[0]['pm_year']
                              ]}

    @http.route(['/my/charts/product_category/current_month'], type='json', auth="user", website=True, csrf=False)
    def product_category_for_current_month(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method provides the Pie chart for the invoices for the products categories of the current month
                     with the condition as per the query.
        """
        
        this_month_query = """
                SELECT 
                    COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS cm_quantity,
                    pg.name AS categ_name 
                FROM 
                    account_move_line aml
                    LEFT JOIN account_move am ON am.id = aml.move_id
                        LEFT JOIN product_product pp ON pp.id = aml.product_id
                        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                        LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
                        LEFT JOIN uom_uom uom_template ON uom_template.id = pt.uom_id
                        LEFT JOIN product_category pg ON pg.id = pt.categ_id
                WHERE 
                    (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s)) 
                        AND am.state = 'posted'
                        AND am.invoice_date  >= date_trunc('month', timezone('America/Mexico_City', now()))::date
                        AND aml.display_type = 'product'
                        AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                        AND aml.account_id IS NOT NULL
                GROUP BY 
                    pg.name;
                """% (request.env.user.partner_id.id,request.env.user.partner_id.id)
        request._cr.execute(this_month_query)
        this_month_data = request._cr.dictfetchall()
        unit_data = []
        categ_data = []
        for rec in this_month_data:
            if rec.get('cm_quantity')>0:
                unit_data.append(rec.get('cm_quantity'))
                categ_data.append(rec.get('categ_name'))

        return {'unit_data': unit_data ,
                'categ_data': categ_data}

    @http.route(['/my/charts/product_category/last_month'], type='json', auth="user", website=True,
                csrf=False)
    def product_category_for_last_month(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method provides the Pie chart for the invoices for the products categories of the last month
                     with the condition as per the query.
        """
        last_month_query = """
                    SELECT 
                        COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS lm_quantity,
                        pg.name AS lm_categ_name 
                    FROM 
                        account_move_line aml
                        LEFT JOIN account_move am ON am.id = aml.move_id
                        LEFT JOIN product_product pp ON pp.id = aml.product_id
                        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                        LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
                        LEFT JOIN uom_uom uom_template ON uom_template.id = pt.uom_id
                        LEFT JOIN product_category pg ON pg.id = pt.categ_id
                    WHERE 
                        (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s)) 
                        AND am.state = 'posted'
                        AND am.invoice_date  < date_trunc('month', timezone('America/Mexico_City', now()))::date 
                        AND am.invoice_date  >=  date_trunc('month', timezone('America/Mexico_City', now() - interval '1' month))::date
                        AND aml.display_type = 'product'
                        AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                        AND aml.account_id IS NOT NULL
                    GROUP BY 
                        pg.name;
                    """ % (request.env.user.partner_id.id, request.env.user.partner_id.id)
        request._cr.execute(last_month_query)
        last_month_data = request._cr.dictfetchall()
        unit_data = []
        categ_data = []
        for rec in last_month_data:
            if rec.get('lm_quantity') > 0:
                unit_data.append(rec.get('lm_quantity'))
                categ_data.append(rec.get('lm_categ_name'))

        return {'unit_data': unit_data,
                'categ_data': categ_data}

    @http.route(['/my/charts/product_category/last_quater'], type='json', auth="user", website=True,
                csrf=False)
    def product_category_for_last_quater(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method provides the Pie chart for the invoices for the products categories of the last quarter month
                     with the condition as per the query.
        """
        last_quater_query = """
                        SELECT 
                            COALESCE(sum(aml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)),0) AS lq_quantity,
                            pg.name AS lq_categ_name 
                        FROM 
                            account_move_line aml
                            LEFT JOIN account_move am ON am.id = aml.move_id
                            LEFT JOIN product_product pp ON pp.id = aml.product_id
                            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                            LEFT JOIN uom_uom uom_line ON uom_line.id = aml.product_uom_id
                            LEFT JOIN uom_uom uom_template ON uom_template.id = pt.uom_id
                            LEFT JOIN product_category pg ON pg.id = pt.categ_id
                        WHERE 
                            (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s)) 
                            AND am.state = 'posted'
                            AND am.invoice_date  < date_trunc('quarter', timezone('America/Mexico_City', now() - interval '3' month)+ interval '3' month ) 
                            AND am.invoice_date  >= DATE_TRUNC('quarter', timezone('America/Mexico_City', now() - interval '3' month))  
                            AND aml.display_type = 'product'
                            AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                            AND aml.account_id IS NOT NULL
                        GROUP BY 
                            pg.name;
                        """ % (request.env.user.partner_id.id, request.env.user.partner_id.id)
        request._cr.execute(last_quater_query)
        last_quater_data = request._cr.dictfetchall()
        unit_data = []
        categ_data = []
        for rec in last_quater_data:
            if rec.get('lq_quantity') > 0:
                unit_data.append(rec.get('lq_quantity'))
                categ_data.append(rec.get('lq_categ_name'))

        return {'unit_data': unit_data,
                'categ_data': categ_data}

    @http.route(['/my/charts/payments'], type='json', auth="user", website=True,csrf=False)
    def payment_status_of_current_month(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method provides the tabular format of invoices which includes :
                     Preparation all invoice as per the current month,
                     Preparation of invoices those are paid after due date and 
                     Preparation of invoices those are paid on time
        """
        start_date = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = (start_date + relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Preapre all invoice as per the current month
        all_paid_invoice_query = """
                select count(*) as all_invoice from account_move am
                where (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s))
                and payment_state = 'paid' and invoice_date_due >= '%s' and invoice_date_due < '%s'
                """ % (
        request.env.user.partner_id.id, request.env.user.partner_id.id, start_date.date(), end_date.date())
        request._cr.execute(all_paid_invoice_query)
        all_paid_invoice_data = request._cr.dictfetchall()

        # Prepare invoices those are paid after due date
        paid_after_due_date_query = """
                select count(*) as after_due_date from account_move am
                where (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s))
                and payment_state = 'paid' and invoice_date_due >= '%s' and invoice_date_due < '%s'
                and payment_date > invoice_date_due
                """ % (
        request.env.user.partner_id.id, request.env.user.partner_id.id, start_date.date(), end_date.date())
        request._cr.execute(paid_after_due_date_query)
        paid_after_due_date_data = request._cr.dictfetchall()

        # Prepare invoices those are paid on time
        paid_on_time_query = """
                select count(*) as on_time from account_move am
                where (am.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s))
                and payment_state = 'paid' and invoice_date_due >= '%s' and invoice_date_due < '%s'
                and payment_date <= invoice_date_due
                """ % (
        request.env.user.partner_id.id, request.env.user.partner_id.id, start_date.date(), end_date.date())
        request._cr.execute(paid_on_time_query)
        paid_on_time_data = request._cr.dictfetchall()
        if all_paid_invoice_data[0].get('all_invoice'):
            return {'paid_on_time': round(
                (paid_on_time_data[0].get('on_time') / all_paid_invoice_data[0].get('all_invoice') * 100), 2),
                    'paid_after_due_date': round((paid_after_due_date_data[0].get('after_due_date') /
                                                  all_paid_invoice_data[0].get('all_invoice') * 100), 2)}
        return {}


    @http.route(['/my/charts/internal_operation'], type='json', auth="user", website=True,
                csrf=False)
    def internal_operation_data(self, **kwargs):
        """
            Authour: nidhi@setconsulting.com
            Date: 28/03/25
            Task: Migration from V16 to V18 
            Purpose: This method provides bar graph which includes the Preparation of data for the picking data as per the last and current month
        """
        # Prepare A data for the picking data as per the last and current month
        internal_operation_query = """
        select sale_order_month_name,sale_order_date,delivery_time,count(delivery_time) from (
            select adt.sale_order_date,
            adt.sale_order_month_name,
            case when (adt.picking+adt.invoicing+adt.delivery+adt.additional_time)/9.0 < 1.0 then '1'
            when (adt.picking+adt.invoicing+adt.delivery+adt.additional_time)/9.0 between 1.0 AND 3.0 then '2'
            when (adt.picking+adt.invoicing+adt.delivery+adt.additional_time)/9.0 between 3.0 AND 6.0 then '3'
            else '4'end as delivery_time
        from (
            select
                sp.name,
                case when sp.x_studio_detener_factura then '3.5'
                else sp.date_invoice_preparation_date_diff end as "additional_time",sp.confirm_date_done_diff as picking ,
                sp.date_done_date_invoice_diff as invoicing,
                sp.preparation_date_shipping_date_diff as delivery,
                EXTRACT(MONTH FROM so.date_order) as sale_order_date,
                TO_CHAR(so.date_order, 'Mon YYYY') as sale_order_month_name
            from stock_picking sp
            inner join sale_order so on so.id = sp.sale_id
            inner join account_move inv_d on inv_d.id = so.invoice_ref_id
            inner join stock_picking_type spt on spt.id = sp.picking_type_id
                where spt.code = 'outgoing' and sp.state= 'done'
                and (so.partner_id IN (SELECT id FROM res_partner WHERE parent_id = %s OR id = %s))
                and so.state in ('sale','done')
                and so.date_order >= date_trunc('month', timezone('America/Mexico_City', now() - interval '1' month))
                and (sp.confirm_date_done_diff > 0 or sp.date_done_date_invoice_diff > 0 or sp.date_invoice_preparation_date_diff > 0 or sp.preparation_date_shipping_date_diff > 0 or sp.shipping_date_delivery_date_diff > 0)
            )as adt
        ) as main group by main.sale_order_date,main.delivery_time,main.sale_order_month_name;
        """% (request.env.user.partner_id.id, request.env.user.partner_id.id)

        request._cr.execute(internal_operation_query)
        internal_operation_data = request._cr.dictfetchall()
        months = list(set(d['sale_order_month_name'] for d in internal_operation_data))
        output = {}
        for delivery_time in set(item['delivery_time'] for item in internal_operation_data):
            output[delivery_time] = [0] * len(months)

        for item in internal_operation_data:
            month_index = months.index(item['sale_order_month_name'])
            output[item['delivery_time']][month_index] = item['count']
        return {
            'one': output.get('1',[0,0]),
            'one_three':output.get('2',[0,0]),
            'three_six':output.get('3',[0,0]),
            'six':output.get('4',[0,0]),
            'months': months
        }