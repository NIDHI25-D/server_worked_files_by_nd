--create schema if not exists datastudio_reports AUTHORIZATION odoo14_datastudio;
--DROP view IF EXISTS datastudio_reports.get_product_template_stock_info_view;
CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.get_product_template_stock_info_materialized_view as
WITH RECURSIVE c AS (
                                                   SELECT id, location_id, id as tmp
                                                        from public.stock_location
                                                   UNION ALL
                                                   SELECT c.id, sa.location_id, c.location_id as tmp
                                                   FROM public.stock_location AS sa
                                                      JOIN c ON c.location_id = sa.id
                                            )

                                            select
                                                ofd.tmpl_id,
                                                ofd.product_id,
                                                sum(quantity) as on_hand,
                                                sum(quantity + incoming_qty - outgoing_qty) as forecast_qty
                                                From(
                                                    select
                                                       pt.id as tmpl_id,
                                                       pp.id as product_id,
                                                       0 as quantity,
                                                       0 as reserved_quantity,
                                                       0 as "incoming_qty",
                                                       0 as outgoing_qty
                                                    from
                                                    public.product_product pp join public.product_template pt on  pt.id = pp.product_tmpl_id
                                                    where pp.active = 't'
                                                    union all
                                                    SELECT
                                                       pt.id as tmpl_id,
                                                       sm.product_id,
                                                       0 as quantity,
                                                       0 as reserved_quantity,
                                                       sum("sm"."product_qty") AS "incoming_qty",
                                                       0 as outgoing_qty
                                                    FROM public."stock_move" as sm
                                                      LEFT JOIN public."stock_location" AS sml ON (sm.location_id = sml.id)
                                                      LEFT JOIN public."stock_location" AS "smld" ON (sm.location_dest_id = smld.id)
                                                      right join public.product_product pp on pp.id = sm.product_id
                                                      join public.product_template pt on pt.id = pp.product_tmpl_id
                                                    WHERE sm."state" in ('waiting', 'confirmed', 'assigned', 'partially_available') and pp.active = 't'
                                                       AND smld.usage='internal' AND sml.usage!='internal'
                                                    GROUP BY sm.product_id, pt.id

                                                    union all
                                                    SELECT
                                                       pt.id as tmpl_id,
                                                       sm.product_id,
                                                       0 as quantity,
                                                       0 as reserved_quantity,
                                                       0 as incoming_quantity,
                                                       sum("sm"."product_qty") AS "outgoing_qty"
                                                    FROM public."stock_move" as sm
                                                      LEFT JOIN public."stock_location" AS sml ON (sm.location_id = sml.id)
                                                      LEFT JOIN public."stock_location" AS "smld" ON (sm.location_dest_id = smld.id)
                                                      right join public.product_product pp on pp.id = sm.product_id
                                                      join public.product_template pt on pt.id = pp.product_tmpl_id
                                                    WHERE sm."state" in ('waiting', 'confirmed', 'assigned', 'partially_available')
                                                       AND sml.usage = 'internal' AND smld.usage != 'internal' AND pp.active = 't'
                                                    GROUP BY sm.product_id, pt.id

                                                    union all
                                                    SELECT
                                                      pt.id as tmpl_id,
                                                      sq.product_id,
                                                      sum(sq.quantity) AS "quantity",
                                                      sum(sq.reserved_quantity) AS "reserved_quantity",
                                                      0 as incoming_qty,
                                                      0 as outgoing_qty
                                                    from public.stock_quant sq
                                                        left join public.stock_location sl on sq.location_id = sl.id
															join c on c.id = sl.id
                                                            join public.stock_warehouse sw on sw.view_location_id = c.tmp-- (select tmp from c where c.id = sl.id)
                                                            right join public.product_product pp on pp.id = sq.product_id
                                                            join public.product_template pt on pt.id = pp.product_tmpl_id
                                                    where  sl.usage='internal'
                                                        and pp.active = 't'
                                                    GROUP BY sq.product_id,pt.id
                                                )ofd

                                                group by ofd.tmpl_id,ofd.product_id;

ALTER TABLE datastudio_reports.get_product_template_stock_info_materialized_view
  OWNER TO odoo14_datastudio;