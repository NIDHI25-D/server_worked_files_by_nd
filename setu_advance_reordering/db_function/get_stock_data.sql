DROP FUNCTION if exists public.get_stock_data_ar(integer[], integer[], integer[], integer[], text, date, date);
CREATE OR REPLACE FUNCTION public.get_stock_data_ar(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN transaction_type text,
    IN start_date date,
    IN end_date date)
  RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, warehouse_id integer, warehouse_name character varying, product_qty numeric, sales_days numeric) AS
$BODY$
DECLARE
     source_usage text[];
    dest_usage text[];
    tr_start_date timestamp without time zone := (start_date || ' 00:00:00')::timestamp without time zone;
    tr_end_date timestamp without time zone:= (end_date || ' 23:59:59')::timestamp without time zone;
BEGIN
    source_usage := case
                when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out', 'internal_in','purchase_return')
                    then '{"internal"}'
                when transaction_type = 'purchase' then '{"supplier"}'
                when transaction_type = 'transit_in' then '{"transit"}'
                when transaction_type = 'adjustment_in' then '{"inventory"}'
                when transaction_type = 'production_in' then '{"production"}'
                when transaction_type = 'sales_return' then '{"customer"}'
            end;
    dest_usage := case
                when transaction_type in ('purchase','transit_in','adjustment_in','production_in', 'internal_in', 'internal_out', 'sales_return')
                     then '{"internal"}'
                when transaction_type = 'sales' then '{"customer"}'
                when transaction_type = 'transit_out' then '{"transit"}'
                when transaction_type = 'adjustment_out' then '{"inventory"}'
                when transaction_type = 'production_out' then '{"production"}'
                when transaction_type = 'purchase_return' then '{"supplier"}'
            end;

    RETURN QUERY
    Select
        T.company_id,
        T.company_name,
        T.product_id,
        T.product_name,
        T.category_id,
        T.category_name,
        T.warehouse_id,
        T.warehouse_name,
        coalesce(sum(T.product_qty),0) as product_qty,
        T.sales_days as sales_days
        From (Select
                foo.company_id,
                foo.company_name,
                foo.product_id,
                foo.product_name,
                foo.category_id,
                foo.category_name,
                foo.warehouse_id,
                foo.warehouse_name,
                coalesce(sum(foo.product_qty),0) as product_qty,
                foo.order_date,
                count(foo.order_date) OVER (PARTITION BY foo.company_id, foo.product_id, foo.category_id, foo.warehouse_id)::numeric AS sales_days
    From
    (
        Select
            move.company_id,
            cmp.name as company_name,
            move.product_id as product_id,
            prod.default_code as product_name,
            tmpl.categ_id as category_id,
            cat.complete_name as category_name,
            so.date_order::date as order_date,
            case when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out', 'purchase_return') then
                source_warehouse.id else  dest_warehouse.id end as warehouse_id,
            case when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out', 'purchase_return') then
                source_warehouse.name else  dest_warehouse.name end as warehouse_name,
            move.product_uom_qty as product_qty
        From
            stock_move move
                Inner Join sale_order_line sol on sol.id = move.sale_line_id
                Inner join sale_order so on so.id = sol.order_id
                Inner Join stock_location source on source.id = move.location_id
                Inner Join stock_location dest on dest.id = move.location_dest_id
                Inner Join res_company cmp on cmp.id = move.company_id
                Inner Join product_product prod on prod.id = move.product_id
                Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                Inner Join product_category cat on cat.id = tmpl.categ_id
                Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
        where prod.active = true and tmpl.active = true
        and source.usage = any(source_usage) and dest.usage = any(dest_usage)
        and move.date::date >= tr_start_date and move.date::date <= tr_end_date
        and move.state = 'done'
        and tmpl.is_storable = True
        and tmpl.type != 'combo'

        --company dynamic condition
        and 1 = case when array_length(company_ids,1) >= 1 then
            case when move.company_id = ANY(company_ids) then 1 else 0 end
            else 1 end
        --product dynamic condition
        and 1 = case when array_length(product_ids,1) >= 1 then
            case when move.product_id = ANY(product_ids) then 1 else 0 end
            else 1 end
        --category dynamic condition
        and 1 = case when array_length(category_ids,1) >= 1 then
            case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
            else 1 end
        --warehouse dynamic condition
        and 1 = case when array_length(warehouse_ids,1) >= 1 then
                case when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out','purchase_return'	) then
                    case when source_warehouse.id = ANY(warehouse_ids) then 1 else 0 end
                else
                    case when dest_warehouse.id = ANY(warehouse_ids) then 1 else 0 end
                end
            else 1 end


        union all


        select
            pso.company_id as company_id,
            cmp.name as company_name,
            pol.product_id as product_id,
            prod.default_code as product_name,
            tmpl.categ_id as category_id,
            cat.complete_name as category_name,
            pso.date_order::date as order_date,
--            case when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out', 'purchase_return') then
--                source_warehouse.id else dest_warehouse.id end as warehouse_id,
            spt.warehouse_id as warehouse_id,
--            case when transaction_type in ('sales','transit_out','production_out','internal_out', 'adjustment_out', 'purchase_return') then
--                source_warehouse.name else dest_warehouse.name end as warehouse_name,
            sw.name as warehouse_name,
            pol.qty as qty

           from
                pos_order_line pol
                join pos_order pso on pso.id = pol.order_id
                join pos_session ps on ps.id = pso.session_id
                join pos_config pc on pc.id = ps.config_id
                join stock_picking_type spt on spt.id = pc.picking_type_id
                join stock_warehouse sw on sw.id = spt.warehouse_id
                Join res_company cmp on cmp.id = pso.company_id
                Join product_product prod ON pol.product_id = prod.id
                Join product_template tmpl ON prod.product_tmpl_id = tmpl.id
                Join product_category cat on cat.id = tmpl.categ_id
--                Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
--                Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                WHERE pso.state::text = ANY (ARRAY['paid'::character varying::text,'invoiced'::character varying::text, 'done'::character varying::text])
                and (coalesce(prod.capping_qty,0) = 0.0 or pol.qty <= coalesce(prod.capping_qty,0))
                and pso.date_order::date >= tr_start_date and pso.date_order::date <= tr_end_date

                --company dynamic condition
                and 1 = case when array_length(company_ids,1) >= 1 then
                case when pso.company_id = ANY(company_ids) then 1 else 0 end
                else 1 end

                --product dynamic condition
                and 1 = case when array_length(product_ids,1) >= 1 then
                case when pol.product_id = ANY(product_ids) then 1 else 0 end
                else 1 end

                --category dynamic condition
                and 1 = case when array_length(category_ids,1) >= 1 then
                case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                else 1 end

                --warehouse dynamic condition
                and 1 = case when array_length(warehouse_ids,1) >= 1 then
                case when spt.warehouse_id = ANY(warehouse_ids) then 1 else 0 end
                else 1 end

        union all


        Select
                    move.company_id,
                    cmp.name as company_name,
                    move.product_id as product_id,
                    prod.default_code as product_name,
                    tmpl.categ_id as category_id,
                    cat.complete_name as category_name,
                    move.date::date as order_date,
                    case when transaction_type in ('sales') then source_warehouse.id
                        when transaction_type in ('sales_return') then  dest_warehouse.id end as warehouse_id,
                    case when transaction_type in ('sales') then  source_warehouse.name
                        when transaction_type in ('sales_return') then dest_warehouse.name end as warehouse_name,
                    (move.product_uom_qty)  as product_qty
                From stock_move move
                        Inner Join stock_location source on source.id = move.location_id
                        Inner Join stock_location dest on dest.id = move.location_dest_id
                        Inner Join res_company cmp on cmp.id = move.company_id
                        Inner Join product_product prod on prod.id = move.product_id
                        Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                        Inner Join product_category cat on cat.id = tmpl.categ_id
                        Inner Join stock_picking_type spt on spt.id = move.picking_type_id
                        Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                        Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                where prod.active = true and tmpl.active = true
--                and source.usage = (case
--                        when transaction_type in ('sales')
--                            then 'internal'
--                        when transaction_type = 'sales_return' then 'inventory' end)
--
--                and dest.usage = (case
--                        when transaction_type in ('sales')
--                            then 'inventory'
--                        when transaction_type = 'sales_return' then 'internal' end)
                and spt.is_considering_in_real_demand = true
                and move.date::date >= tr_start_date and move.date::date <= tr_end_date
                and move.state = 'done'
                and tmpl.is_storable = True
                and tmpl.type != 'combo'

                --company dynamic condition
                and 1 = case when array_length(company_ids,1) >= 1 then
                    case when move.company_id = ANY(company_ids) then 1 else 0 end
                    else 1 end
                --product dynamic condition
                and 1 = case when array_length(product_ids,1) >= 1 then
                    case when move.product_id = ANY(product_ids) then 1 else 0 end
                    else 1 end
                --category dynamic condition
                and 1 = case when array_length(category_ids,1) >= 1 then
                    case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                    else 1 end
                --warehouse dynamic condition
                and 1 = case when array_length(warehouse_ids,1) >= 1 then
                        case when transaction_type in ('sales') then
                            case when source_warehouse.id = ANY(warehouse_ids) then 1 else 0 end
                        when  transaction_type in ('sales_return') then
                            case when dest_warehouse.id = ANY(warehouse_ids) then 1 else 0 end
                        end
                    else 1 end
    )foo
    group by foo.company_id, foo.product_id, foo.category_id, foo.warehouse_id, foo.company_name, foo.product_name, foo.category_name, foo.warehouse_name, foo.order_date

    )T
    group by T.company_id, T.company_name, T.product_id, T.product_name,T.category_id, T.category_name, T.warehouse_id, T.warehouse_name, T.sales_days
    ;
END; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;

--, T.order_date
--select * from get_stock_data_ar('{}','{79935}','{}','{}','sales','2021-01-01','2023-07-30')
