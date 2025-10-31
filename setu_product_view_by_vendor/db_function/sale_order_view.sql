--create schema if not exists datastudio_reports AUTHORIZATION odoo14_datastudio;
--DROP view IF EXISTS datastudio_reports.view_of_sale_order;
CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.materialized_view_of_sale_order as
with invoice_count as(select sol.order_id as order_id,
	case when  aml.move_id = mv.id then 1
	else count(mv.id) end as invoice_name
	from public.account_move mv
	join public.account_move_line aml on aml.move_id= mv.id
	right join public.sale_order_line_invoice_rel solir on solir.invoice_line_id = aml.id
	join public.sale_order_line sol on sol.id = solir.order_line_id
	join public.sale_order so on sol.order_id = so.id
 group by mv.id,aml.move_id,sol.order_id),
field_value as (select imf.name,imfs.value,regexp_replace(to_json(imfs.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g') as field_value from public.ir_model im
		join public.ir_model_fields imf on imf.model_id = im.id
		join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
		where im.model = 'sale.order' and imf.name in ('state', 'picking_policy', 'invoice_status', 'l10n_mx_edi_usage')),

preparation_date_from_picking as (select so.id so , sp.id, sp.preparation_date pd ,sp.date_done , sp.create_date, row_number() over(partition by so.id order by sp.date_done asc) from
        public.sale_order so
        left join public.stock_picking sp on sp.sale_id = so.id  and sp.state = 'done'
        left join public.stock_picking_type spt on spt.id = sp.picking_type_id and spt.code = 'outgoing'
  order by so.id, sp.date_done asc  )
select
	so.id as id,
	so.meli_order_id as meli_order_id,
    so.create_date as create_date,
	so.partner_id as partner_id,
	so.partner_invoice_id as partner_invoice_id,
	so.partner_shipping_id as partner_shipping_id,
    trim((select field_value from field_value where name = 'state' and value =  so.state ))as "Status",
	max(r_id) as "Delivery",
	sum(inn.invoice_name) as "Invoice",
	so.name as "Order_Number",
	rs.name as "Customer_Name",
	rsi.name as "Invoice_Address",
	rsd.name as "Delivery_Address",
	(SELECT ((so.date_order) AT TIME ZONE 'UTC')::timestamp) as "Quotation_Date",
	so.pricelist_id as "Public_Pricelist_ID",
	trim((select regexp_replace(to_json(ppl.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as "Public_Pricelist_Name",
	so.payment_term_id as "Payment_Term_id",
	trim((select regexp_replace(to_json(apt.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as "Payment_Term",
	so.mostrador as "Cliente_Mostrador",
	so.dfactura as "Detener_envio",
	rs.warehouse_sugerido_id as "Surtido_Sugerido_id",
	swsug.name as "Surtido_Sugerido",
	so.user_id as "sale_Person_Id",
	resp.name as "Sale_Person_Name",
	so.team_id as "Sale_Team_Id",
	trim((select regexp_replace(to_json(ct.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as "Sale_Team_Name",
	so.require_signature as "Online_Signature",
	so.require_payment as "Online_Payment",
	so.client_order_ref as "Customer_Reference",
	so.warehouse_id as "Warehouse_Id",
	sw.name as "Warehouse_Name",
	trim((select field_value from field_value where name = 'picking_policy' and value = so.picking_policy ))as "Shipping_Policy",
	(SELECT ((so.commitment_date) AT TIME ZONE 'UTC')::timestamp) AS "Delivery_Date",
	so.effective_date::date as "Effective_Date",

	so.fiscal_position_id as "Fiscal_Position_Id",
	trim((select regexp_replace(to_json(afp.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as "Fiscal_Position_Name",
	-- so.analytic_account_id as "Analytic_Account_Id", <-- remove field
	-- aaa.name as "Analytic_Account_Name",
    trim((select field_value from field_value where name = 'invoice_status' and value =so.invoice_status )) as "Invoice_Status",
	so.l10n_mx_edi_payment_method_id "Payment_Way_Id",
	lpy.name as "Payment_Way_Name",
	trim((select field_value from field_value where name = 'l10n_mx_edi_usage' and value = so.l10n_mx_edi_usage ))as "Usage",
	so.origin as "Source_Document",
	ppdf.pd as  "Preparation_Date",

	so.opportunity_id as "Opportunity_Id",
	cl.name as "Opportunity",
	so.campaign_id as "Campaig_Id",
	uc.name as "Campaign",
	so.medium_id as "Medium_Id",
	um.name as "Medium",
	so.source_id as "Source_Id",
	us.name as "Source",
	so.amount_untaxed as "Untaxed_Amount",
	so.amount_tax as "Taxes",
	so.amount_total as "Total",
	so.margin as "Margin",
	COALESCE(so.is_monthly_proposal, 'f') as is_monthly,
	so.is_from_website as is_from_website,
 	coalesce(so.is_preorder, false)as "is_preorder",
 	coalesce(so.is_presale, false) as "is_presale",
	socp.promo_program as "promo_program",
	STRING_AGG(distinct trim((select regexp_replace(to_json(crm.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))),',') as "tags",

	CAST(1/so.currency_rate AS DECIMAL(5, 2)) as "Currency_Rate",
	string_agg(distinct mc.name,',') as clasificaciones,
	string_agg(distinct ms.name,',') as subclases
	from public.sale_order so
	left join invoice_count inn on inn.order_id = so.id
	left join (
		select
		count(id) as r_id,
		sale_id
		from public.stock_picking
		group by sale_id
	)sp1 on sp1.sale_id = so.id
	left join public.res_partner rs on rs.id = so.partner_id
	left join public.stock_warehouse swsug on  swsug.id = rs.warehouse_sugerido_id
	left join public.res_partner rsi on rsi.id = so.partner_invoice_id
	left join public.res_partner rsd on rsd.id = so.partner_shipping_id
	left join public.product_pricelist ppl on ppl.id = so.pricelist_id
	left join public.account_payment_term apt on apt.id = so.payment_term_id
	left join public.res_users ru on ru.id = so.user_id
	left join public.res_partner resp on resp.id = ru.partner_id
	left join public.crm_team ct on ct.id = so.team_id
	left join public.stock_warehouse sw on sw.id = so.warehouse_id
	left join public.account_fiscal_position afp on afp.id = so.fiscal_position_id
	-- left join public.account_analytic_account aaa on so.analytic_account_id = aaa.id
	left join public.l10n_mx_edi_payment_method lpy on so.l10n_mx_edi_payment_method_id = lpy.id
	left join public.crm_lead cl on so.opportunity_id = cl.id
	left join public.utm_campaign uc on so.campaign_id = uc.id
	left join public.utm_medium um on so.medium_id = um.id
	left join public.utm_source us on so.source_id = us.id
	left join public.sale_order_tag_rel x_crm on x_crm.order_id=so.id
	left join public.crm_tag crm on crm.id=x_crm.tag_id
	left join public.marvelfields_clasificaciones_rel mcr on mcr.src_id=rs.id
	left join public.marvelfields_clasificaciones mc on mc.id=mcr.dest_id
	left join public.marvelfields_subclases_rel msr on msr.src_id=rs.id
	left join public.marvelfields_subclases ms on ms.id=msr.dest_id
	left join preparation_date_from_picking ppdf on ppdf.so = so.id and ppdf.row_number = 1
	left join (
		select
			order_id as sale_id,
			trim(string_agg(lp.name->>'en_US',', ')) as "promo_program"
		from public.loyalty_card lc
			left join public.loyalty_program lp on lp.id = lc.program_id
		group by order_id
	) socp on socp.sale_id = so.id
	group by so.state,so.name,rs.name,rsi.name,rsd.name,so.date_order,so.pricelist_id,ppl.name,so.payment_term_id,
	apt.name,so.mostrador,so.dfactura ,so.user_id,resp.name,so.team_id,ct.name,so.require_signature,so.require_payment,
	so.client_order_ref,so.warehouse_id,sw.name,so.picking_policy,so.commitment_date,so.effective_date,so.fiscal_position_id,
	afp.name,inn.invoice_name, so.name,so.invoice_status,so.l10n_mx_edi_payment_method_id, --aaa.name, so.analytic_account_id ,
	lpy.name,so.l10n_mx_edi_usage,so.origin,so.opportunity_id,cl.name,so.campaign_id,uc.name,so.medium_id,um.name,so.source_id
	,us.name,so.amount_untaxed,so.amount_tax,so.amount_total,so.margin,so.id,rs.warehouse_sugerido_id,swsug.name,ppdf.pd,socp.promo_program;

ALTER TABLE datastudio_reports.materialized_view_of_sale_order
  OWNER TO odoo14_datastudio;