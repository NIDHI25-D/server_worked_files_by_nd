DROP FUNCTION IF EXISTS public.get_out_of_stock_data_day_wise(integer[], integer[], integer[], integer[], date, date);
CREATE OR REPLACE FUNCTION public.get_out_of_stock_data_day_wise(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[],
    IN warehouse_ids integer[],
    IN start_date date,
    IN end_date date)
  RETURNS TABLE(product_id integer, opening_count integer) AS
  -- RETURNS TABLE(row_id bigint, move_date date, warehouse_id integer, product_id integer,opening numeric, closing numeric) AS

$BODY$
BEGIN

    return query


with row_datas as (
select
                    tmp.row_id,
                    tmp.move_date,
                    tmp.product_id,
                    tmp.warehouse_id,
                    sum(tmp.qty_in) as qty_in,
                    sum(tmp.qty_out) as qty_out,
                    SUM(sum(tmp.qty_in)-sum(tmp.qty_out)) OVER (PARTITION BY tmp.warehouse_id , tmp.product_id order by tmp.move_date ROWS UNBOUNDED PRECEDING) AS closing
                from (
                    select
                            row_number() over(partition by foo.warehouse_id, foo.product_id order by foo.move_date) as row_id,
                            foo.move_date,
                            foo.product_id,
                            foo.warehouse_id,
                            case when foo.warehouse_id = int_move_data.dest_warehouse then
                                sum(foo.qty_in) + sum(int_move_data.int_qty)
                            else
                                sum(foo.qty_in) end as qty_in,
                            case when foo.warehouse_id = int_move_data.source_warehouse then
                                sum(foo.qty_out) + sum(int_move_data.int_qty)
                            else
                                sum(foo.qty_out) end as qty_out
                        from (
                        select
                            -- row_number() over(partition by move_data.warehouse_id, move_data.product_id order by move_data.move_date) as row_id,
                            move_data.move_date,
                            move_data.product_id,
                            move_data.warehouse_id,
                            sum(move_data.qty_in)  as qty_in,
                            sum(move_data.qty_out)  as qty_out
                        from (
                                select
                                    generate_series(start_date::date - interval '1 day', end_date::date, '1 day'::interval)::date as move_date,
                                    prod.id AS product_id,
                                    wh.id as warehouse_id,
                                    0 as qty_in,
                                    0 as qty_out
                                from
                                    product_product prod,stock_warehouse wh
                                where
                                    prod.active = true and
									 wh.active = true
                                    and 1 = case when array_length(product_ids,1) >= 1 then
                                    case when prod.id = ANY(product_ids) then 1 else 0 end
                                    else 1 end


                                UNION all

                                select
                                    start_date::date - interval '1 day' as move_date,
                                    move.product_id,
                                    case when dest.usage = 'internal' then
                                        dest_warehouse.id
                                    else
                                        source_warehouse.id end as warehouse_id,

                                    sum(case when dest.usage = 'internal' then
                                        move.product_uom_qty
                                    else
                                        0 end) as qty_in,
                                    sum(case when dest.usage != 'internal' then
                                        move.product_uom_qty
                                    else
                                        0 end) as qty_out

                                from
                                    stock_move move
                                    Inner Join stock_location source on source.id = move.location_id
                                    Inner Join stock_location dest on dest.id = move.location_dest_id
                                    Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                                    Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                                where
                                    move.state = 'done'
                                    and dest.usage != source.usage
                                    --and move.product_id = 53144
                                    and move.date::date <= start_date
                                    and 1 = case when array_length(product_ids,1) >= 1 then
                                    case when move.product_id = ANY(product_ids) then 1 else 0 end
                                    else 1 end


                                group by 1,2,3
                                UNION all

                                select
                                    move.date::date as move_date,
                                    move.product_id,
                                    case when dest.usage = 'internal' then
                                        dest_warehouse.id
                                    else
                                        source_warehouse.id end as warehouse_id,

                                    sum(case when dest.usage = 'internal' then
                                        move.product_uom_qty
                                    else
                                        0 end) as qty_in,
                                    sum(case when dest.usage != 'internal' then
                                        move.product_uom_qty
                                    else
                                        0 end) as qty_out

                                from
                                    stock_move move
                                    Inner Join stock_location source on source.id = move.location_id
                                    Inner Join stock_location dest on dest.id = move.location_dest_id
                                    Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                                    Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                                where
                                    move.state = 'done'
                                    and dest.usage != source.usage
                                   -- and move.product_id = 53144
                                    and move.date::date >= start_date and move.date::date <= end_date
                                        and 1 = case when array_length(product_ids,1) >= 1 then
                                        case when move.product_id = ANY(product_ids) then 1 else 0 end
                                        else 1 end

                                group by 1,2,3

                            )move_data
                                group by 1,2,3)foo

                            left join (select
                                        case when move.date::date < start_date then
                                            start_date::date - interval '1 day'
                                        else
                                            move.date::date
                                            end as move_date,
                                        move.product_id,
                                        source_warehouse.id as source_warehouse,
                                        dest_warehouse.id as dest_warehouse,
                                        COALESCE(move.product_uom_qty,0) as int_qty
                                    from
                                        stock_move move
                                        Inner Join stock_location source on source.id = move.location_id
                                        Inner Join stock_location dest on dest.id = move.location_dest_id
                                        Left Join stock_warehouse source_warehouse ON source.parent_path::text ~~ concat('%/', source_warehouse.view_location_id, '/%')
                                        Left Join stock_warehouse dest_warehouse ON dest.parent_path::text ~~ concat('%/', dest_warehouse.view_location_id, '/%')
                                    where
                                        move.state = 'done'
                                        and dest.usage = source.usage and source_warehouse.id != dest_warehouse.id
                                        --and move.product_id = 53144
                                        -- and move.date::date >= '2024-03-01'
                                        and move.date::date <= end_date
                                        and 1 = case when array_length(product_ids,1) >= 1 then
                                        case when move.product_id = ANY(product_ids) then 1 else 0 end
                                        else 1 end
                                        group by 1,2,3,4,5
                                    )int_move_data on foo.move_date = int_move_data.move_date
                                        and int_move_data.product_id = foo.product_id
                                        and (int_move_data.dest_warehouse = foo.warehouse_id or int_move_data.source_warehouse = foo.warehouse_id)
                                        group by 2,3,4,int_move_data.dest_warehouse, int_move_data.source_warehouse
                                        order by 4,2,3
                                 )tmp where
                                 1 = case when array_length(warehouse_ids,1) >= 1 then
                                    case when tmp.warehouse_id = ANY(warehouse_ids) then 1 else 0 end
                                    else 1 end

                                 group by tmp.row_id,tmp.move_date , tmp.warehouse_id , tmp.product_id),

                  row_table as ( select
                        r2.move_date::date,
                        r1.product_id,
                        sum (case when r1.closing > 0 then r1.closing else 0.0 end) as opening,
                        sum(case when r2.closing > 0 then r2.closing else 0.0 end)  as closing
                    from
                        row_datas r1 join row_datas r2 on r1.product_id = r2.product_id
                                                      and r1.warehouse_id = r2.warehouse_id
                                                      and r1.row_id = r2.row_id-1
                        group by r1.product_id,r2.move_date,r1.move_date
                        having r1.move_date::date >= start_date
                        )
    select row_table.product_id,count(distinct row_table.move_date):: integer from row_table where opening = 0.0
    group by row_table.product_id;

END; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
