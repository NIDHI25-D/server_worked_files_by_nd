DROP FUNCTION IF EXISTS set_inventory_warehouse_wise_data;
CREATE OR REPLACE FUNCTION public.set_inventory_warehouse_wise_data(
    IN company_ids integer[],
    IN warehouse_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[]
)
  RETURNS TABLE(warehouse_id integer, company_id integer, product_id integer, on_hand_stock numeric, available_quantity numeric, current_stock_value numeric, categ_id integer) AS

$BODY$
BEGIN

        delete from inventory_warehouse_report;
        Return Query

select * from (select
	sw.id as warehouse_id,
	sw.company_id as company_id,
	sq.product_id,
	sum(sq.quantity)as on_hand_stock,
	sum(sq.quantity - sq.reserved_quantity) as available_quantity,
	(sum(sq.quantity)*pc.price)as current_stock_value,
	pt.categ_id
from stock_quant sq
left join product_product pp on pp.id = sq.product_id
left join product_template pt on pt.id = pp.product_tmpl_id
left join stock_location sl on sl.id = sq.location_id
left join stock_warehouse sw on sl.parent_path::text ~~ concat('%/', sw.view_location_id, '/%')
left join (
	select costing.product_id,(costing.value/costing.quantity)as price from
	(select
		svl.product_id,
		sum(svl.value)as value,sum(quantity)as quantity
	from stock_valuation_layer svl
	group by svl.product_id)as costing
	where costing.quantity > 0 or costing.quantity < 0
)as pc on pc.product_id = sq.product_id

where sl.usage = 'internal' and pt.type = 'consu'
group by
	sw.id,
	sq.product_id,
	pt.categ_id,
	pc.price)as vh where vh.on_hand_stock != 0;
END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;