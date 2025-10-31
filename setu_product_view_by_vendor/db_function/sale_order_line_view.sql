--create schema if not exists datastudio_reports AUTHORIZATION odoo14_datastudio;
--DROP view IF EXISTS datastudio_reports.view_of_sale_order_line;
CREATE MATERIALIZED VIEW IF NOT EXISTS datastudio_reports.materialized_view_of_sale_order_line AS

with analytic_account as (
    select id as sale_line_id,
           array_agg(x.cola::integer) as analytic_distribution_ids,
           array_to_string(array_agg(x.colb), ',') as analytic_distribution
            -- x.name as name
    from public.sale_order_line sale_line
    cross join lateral json_each(sale_line.analytic_distribution::json) as x(cola, colb) where sale_line.analytic_distribution is not null
    group by id
)

select
            sol.id as id,
            sol.order_id as "Sale_Order_Id",
            so.name as "Sale_order",
            pp.default_code as prod_internal_ref,

            sol.route_id as "Route_Id",
            slr.name as "Route_name",
            sol.product_uom_qty as "Ordered_QTY",
            sol.qty_delivered as "Delivered_Qty",
            sol.qty_invoiced as "Invoiced_Qty",
            sol.price_unit as "Unit_price",
            sol.purchase_price as "Cost",
            sol.margin as "Margin",
            round((sol.margin_percent *100)::numeric,2) as "Margin_Percentage",

			STRING_AGG(distinct trim((select regexp_replace(to_json(act.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))),', ') as "account_tax",
            -- STRING_AGG(distinct act.name,','),
            sol.discount as "Discount",
            sol.price_total as "Total",
            coalesce(sol.is_preorder, false)as "is_preorder",
            coalesce(sol.is_presale, false) as "is_presale",
			case when sol.reward_id is not null then cast('t' as boolean) else cast('f' as boolean) end as "reward_line",
			trim(regexp_replace(to_json(lp.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
             as "promo_program",
            CAST(1/so.currency_rate AS DECIMAL(5, 2)) as "Currency_Rate",
            case when lp.name is not null then cast('t' as boolean) else cast('f' as boolean) end as "is_promo_program",
			(SELECT ((so.date_order) AT TIME ZONE 'UTC')::timestamp) as "quotation_date",
            aa.analytic_account_ids as analytic_account_ids,
			aa.analytic_account_names as analytic_account_names

            from public.sale_order so
            left join public.sale_order_line sol on so.id = sol.order_id
            left join public.product_product pp on pp.id = sol.product_id
            left join public.account_tax_sale_order_line_rel ttn on ttn.sale_order_line_id = sol.id
            left join public.account_tax act on act.id = ttn.account_tax_id
            left join public.stock_route slr on slr.id = sol.route_id
            left join public.loyalty_card lc on lc.id = sol.coupon_id
	        left join public.loyalty_program lp on lp.id = lc.program_id
	        LEFT JOIN analytic_account account ON account.sale_line_id=sol.id
            left join lateral (
			select
				string_agg(trim(regexp_replace(to_json(aaa.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')), ', ') as analytic_account_names,
				string_agg(aaa.id::text, ',') as analytic_account_ids
			from public.account_analytic_account aaa
			where aaa.id = any(account.analytic_distribution_ids)
		) as aa on true
            where so.date_order >= '2022-01-01 06:00:00'
		   group by  sol.id , sol.order_id ,
            so.name,
            pp.default_code ,
            sol.route_id ,
            slr.name ,
            sol.product_uom_qty,
            sol.qty_delivered,
            sol.qty_invoiced ,
            sol.price_unit ,
            sol.purchase_price ,
            sol.margin ,
           sol.margin_percent  ,

            sol.discount ,
            sol.price_total ,sol.create_date,lp.name,so.date_order,so.currency_rate, aa.analytic_account_names,aa.analytic_account_ids
           order by sol.create_date desc;

ALTER TABLE datastudio_reports.materialized_view_of_sale_order_line
  OWNER TO odoo14_datastudio;
