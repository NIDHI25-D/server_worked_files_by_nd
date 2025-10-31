DROP FUNCTION IF EXISTS get_sales_time_data(date, date, integer);
--DROP FUNCTION IF EXISTS get_sales_time_data(datetime, datetime);
    CREATE OR REPLACE FUNCTION public.get_sales_time_data(
    IN start_date date,
    IN end_date date,
    IN wizard_id integer)
   RETURNS VOID  AS
$BODY$
BEGIN
        wizard_id := wizard_id;
        DELETE FROM sales_time_dashboard;
        Insert into sales_time_dashboard(wizard_id, create_sale_order_date, created_user_id, so_name, picking_name, is_created_from_website, actual_hours_to_confirm_so, actual_hours_to_confirm_so_by_customer, actual_hours_to_create_picking, actual_hours_to_create_invoice, actual_hours_to_prepare_picking, actual_hours_to_delivery, actual_hours_to_send_order, actual_total_time_taken, cliente_mostrador, partner_id, team_id, detener_envio, carrier_id, payment_term_id, payment_status, payment_state, date_order_received, preparation_date, x_studio_fecha_de_envio, x_studio_fecha_de_entrega, carrier_tracking_ref, delivery_cost)
        select wizard_id,T.order_date,T.create_user_id, T.order_id, T.picking_id, T.website, T.actual_hours_to_confirm_so, T.actual_hours_to_confirm_so_by_customer, T.actual_hours_to_create_picking, T.actual_hours_to_create_invoice, T.actual_hours_to_prepare_picking, T.actual_hours_to_delivery, T.actual_hours_to_send_order, T.actual_total_time_taken, T.cliente_mostrador, T.partner_id, T.team_id, T.dfactura, T.carrier_id, T.payment_term_id, T.payment_status, T.payment_state, T.date_order_received, T.preparation_date, T.x_studio_fecha_de_envio, T.x_studio_fecha_de_entrega, T.carrier_tracking_ref, T.delivery_cost
        from (


with field_value as (select imf.name,imfs.value,to_json(imfs.name->'en_US'::text)::varchar as field_value from public.ir_model im
		join public.ir_model_fields imf on imf.model_id = im.id
		join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
		where im.model = 'stock.picking' and imf.name in ('payment_state')),
field_values as (select imf.name,imfs.value,to_json(imfs.name->'en_US'::text)::varchar as field_values from public.ir_model im
	join public.ir_model_fields imf on imf.model_id = im.id
	join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
	where im.model = 'account.move' and imf.name in ('payment_state'))

Select  so_n.id as order_id,
	sp.id as picking_id,
	inv_d.id as invoice_id,
    coalesce(so_n.mostrador,false) as cliente_mostrador,
    so_n.partner_id as partner_id ,
    so_n.team_id as team_id,
    coalesce(so_n.dfactura,false) as dfactura,
    sp.carrier_id as carrier_id,
    so_n.payment_term_id as payment_term_id,
	(select field_value from field_value where name = 'payment_state' and value =  sp.payment_state )as "payment_state",
	(select field_values from field_values where name = 'payment_state' and value =  inv_d.payment_state )as "payment_status",
	case when so_n.website_id > 0 then 'Yes' else 'No' end as website,
	coalesce(so_n.create_confirm_diff,0) as actual_hours_to_confirm_so,
	so_n.customer_confirmation_diff as actual_hours_to_confirm_so_by_customer,
	coalesce(sp.confirm_date_done_diff, 0) as actual_hours_to_create_picking,
	coalesce(sp.date_done_date_invoice_diff, 0) as actual_hours_to_create_invoice,
	coalesce(sp.date_invoice_preparation_date_diff, 0) as actual_hours_to_prepare_picking,
	coalesce(sp.preparation_date_shipping_date_diff, 0) as actual_hours_to_delivery,
	coalesce(sp.shipping_date_delivery_date_diff, 0) as actual_hours_to_send_order,
	coalesce(so_n.create_confirm_diff + sp.confirm_date_done_diff + sp.date_done_date_invoice_diff + sp.date_invoice_preparation_date_diff + sp.preparation_date_shipping_date_diff + sp.shipping_date_delivery_date_diff, 0) as actual_total_time_taken,
	sp.date_order_received as date_order_received,
	sp.preparation_date as preparation_date,
	sp.x_studio_fecha_de_envio as x_studio_fecha_de_envio,
	sp.x_studio_fecha_de_entrega as x_studio_fecha_de_entrega,
	sp.carrier_tracking_ref as carrier_tracking_ref,
	sp.delivery_cost as delivery_cost,
	so_n.date_order as order_date,
	so_n.create_uid as create_user_id

    from sale_order so_n
--	Inner join sale_order so_n on so_n.id = am.sale
	Inner join account_move inv_d on inv_d.id = so_n.invoice_ref_id
	Inner join stock_picking sp on sp.sale_id = so_n.id
	Inner join stock_picking_type spt on spt.id = sp.picking_type_id
	where sp.state = 'done' and spt.code = 'outgoing' and so_n.date_order between start_date and end_date and so_n.invoice_ref_id is not null

	order by so_n.id desc)T
	WHERE T.actual_hours_to_confirm_so > 0 or T.actual_hours_to_create_invoice > 0 or T.actual_hours_to_create_picking > 0 or T.actual_hours_to_prepare_picking > 0
	or T.actual_hours_to_delivery > 0 or T.actual_total_time_taken > 0 or T.actual_hours_to_send_order > 0;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;


--select * from get_sales_time_data('2022-01-01','2022-06-30', '1')
