--create schema if not exists datastudio_reports AUTHORIZATION odoo14_datastudio;
--DROP view IF EXISTS datastudio_reports.view_of_product_by_vendor;
CREATE MATERIALIZED  view IF NOT EXISTS datastudio_reports.materialized_view_of_product_by_vendor as
select pp.default_code as prod_internal_ref,
	trim((select regexp_replace((select regexp_replace(to_json(pt.description ->'en_US'::text)::varchar,'<[^>]*>', '', 'g')),'[^%,/\.\w]+',' ','g'))) as description,
	rs.id as vendor_id,
	rs.name as vendor_name,
	ps.product_name as vendor_product_name,
	ps.product_code as vendor_product_code,
	rc.id as currency_id,
	rc.name as currency_name,
	ps.date_start as start_date,
	ps.date_end as end_date,
	ps.min_qty as quantity,
	uu.id as unit_of_measure_id,
	trim((select regexp_replace(to_json(uu.name ->'en_US'::text)::varchar,'[^%,''/\.\w]+',' ','g')))as unit_of_measure_name,
	ps.price as price,
	ps.reorder_minimum_quantity as reorder_minimum_quantity,
	ps.delay as Delivery_Lead
	from public.product_template pt
		left join public.product_product pp on pt.id = pp.product_tmpl_id
		join public.product_supplierinfo ps on ps.product_tmpl_id = pp.product_tmpl_id
		left join public.res_partner rs on ps.partner_id = rs.id
		left join public.res_currency rc on ps.currency_id = rc.id
		left join public.uom_uom uu ON pt.uom_id = uu.id where pp.active = 't';
ALTER TABLE datastudio_reports.materialized_view_of_product_by_vendor
  OWNER TO odoo14_datastudio;