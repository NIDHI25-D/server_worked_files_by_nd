DROP FUNCTION if exists public.inventory_stock_age_report(integer[], integer[], integer[]);
CREATE OR REPLACE FUNCTION public.inventory_stock_age_report(
    IN company_ids integer[],
    IN product_ids integer[],
    IN category_ids integer[])
  RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, current_stock numeric, current_stock_value numeric, oldest_date date, days_old integer, oldest_stock_qty numeric, oldest_stock_value numeric, stock_qty_ratio numeric, stock_value_ratio numeric) AS
$BODY$
    BEGIN
    --
        Drop Table if exists stock_age_table;
        Drop Table if exists final_stock_age_table;
        CREATE TEMPORARY TABLE stock_age_table(
            row_id INT,
            company_id INT,
            company_name character varying,
            in_date date,
            product_id INT,
            product_name character varying,
            product_category_id INT,
            category_name character varying,
            current_stock numeric DEFAULT 0,
            current_stock_value numeric DEFAULT 0,
            days_old numeric DEFAULT 0, stock_qty_ratio numeric DEFAULT 0,stock_value_ratio numeric DEFAULT 0
        );
        CREATE TEMPORARY TABLE final_stock_age_table(
            company_id INT,
            company_name character varying,
            product_id INT,
            product_name character varying,
            product_category_id INT,
            category_name character varying,
	    total_stock numeric DEFAULT 0,
	    total_stock_value numeric DEFAULT 0,
	    in_date date,
	    days_old integer DEFAULT 0,
            current_stock numeric DEFAULT 0,
            current_stock_value numeric DEFAULT 0,
            stock_qty_ratio numeric DEFAULT 0,stock_value_ratio numeric DEFAULT 0
        );
        Insert into stock_age_table
        select
            l.*
        from
                (select
                row_number() over(partition by all_d.company_id, all_d.product_id order by all_d.company_id, all_d.product_id, all_d.move_date) row_id,
                all_d.company_id,all_d.company_name,all_d.move_date, all_d.product_id, all_d.product_code, all_d.category_id, all_d.category_name, sum(stock_qty) as stock_qty, sum(stock_value) as stock_value

                from
                    (
                    Select
                        layer.company_id,
                        cmp.name as company_name,
                        move.date::date as move_date,
                        layer.product_id,
                        concat('['||(prod.default_code||'')||']'||' '||(tmpl.name ->>'en_US'))::character varying as product_code,
                        tmpl.categ_id as category_id,
                        cat.complete_name as category_name,
                        sum(layer.remaining_qty) stock_qty,
                        sum(layer.remaining_value) stock_value
                    from
                        stock_valuation_layer layer
                            left Join stock_move move on move.id = layer.stock_move_id
                            left Join product_product prod on prod.id = layer.product_id
                            left Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                            left Join product_category cat on cat.id = tmpl.categ_id
                            left Join res_company cmp on cmp.id = layer.company_id
                            left join LATERAL get_category_company_dependent() as ls  ON ls.company_id = layer.company_id AND ls.cost_method NOT IN ('standard') AND ls.category_id = cat.id
                        Where remaining_qty > 0 and prod.active = True and tmpl.active = True and --and layer.product_id = 284
                        1 = case when array_length(product_ids,1) >= 1 then
                            case when layer.product_id = ANY(product_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(category_ids,1) >= 1 then
                            case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(company_ids,1) >= 1 then
                            case when layer.company_id = ANY(company_ids) then 1 else 0 end
                            else 1 end
                        group by layer.company_id, cmp.name, move.date, layer.create_date, layer.product_id, prod.default_code, tmpl.name, tmpl.categ_id, cat.complete_name

                    UNION ALL

                    Select
                        layer.company_id,
                        cmp.name as company_name,
                        move.date::date as move_date,
                        layer.product_id,
                        concat('['||(prod.default_code||'')||']'||' '||(tmpl.name ->>'en_US'))::character varying as product_code,
                        tmpl.categ_id as category_id,
                        cat.complete_name as category_name,
                        sum(layer.quantity) stock_qty,
                        sum(layer.value) stock_value
                    from
                        stock_valuation_layer layer
                            Inner Join stock_move move on move.id = layer.stock_move_id
                            Inner Join product_product prod on prod.id = layer.product_id
                            Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                            Inner Join product_category cat on cat.id = tmpl.categ_id
                            Inner Join res_company cmp on cmp.id = layer.company_id
                            Inner join LATERAL get_category_company_dependent() as ls ON ls.company_id = layer.company_id AND ls.cost_method NOT IN ('fifo','average') AND ls.category_id = cat.id
                        Where (remaining_qty is null)
                        and 1 = case when array_length(product_ids,1) >= 1 then
                            case when layer.product_id = ANY(product_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(category_ids,1) >= 1 then
                            case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(company_ids,1) >= 1 then
                            case when layer.company_id = ANY(company_ids) then 1 else 0 end
                            else 1 end
                        and prod.active = True and tmpl.active = True
                        group by layer.company_id, cmp.name, move.date, layer.product_id, prod.default_code, tmpl.name, tmpl.categ_id, cat.complete_name

                    UNION ALL

                    Select
                        layer.company_id as company_id,
                        cmp.name as company_name,
                        layer.create_date as move_date,
                        layer.product_id as product_id,
                        concat('['||(prod.default_code||'')||']'||' '||(tmpl.name ->>'en_US'))::character varying as product_code,
                        tmpl.categ_id as category_id,
                        cat.complete_name as category_name,

                        sum(layer.quantity) as stock_qty,
                        sum(layer.value) stock_value
                    from
                        stock_valuation_layer layer
                            Inner Join product_product prod on prod.id = layer.product_id
                            Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id
                            Inner Join product_category cat on cat.id = tmpl.categ_id
                            Inner Join res_company cmp on cmp.id = layer.company_id
                            Inner Join LATERAL get_category_company_dependent() as ls  ON ls.company_id = layer.company_id AND ls.cost_method NOT IN ('fifo','average') AND ls.category_id = cat.id
                        Where (remaining_qty is null and layer.description ilike '%Product value manually modified%')
                        and 1 = case when array_length(product_ids,1) >= 1 then
                            case when layer.product_id = ANY(product_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(category_ids,1) >= 1 then
                            case when tmpl.categ_id = ANY(category_ids) then 1 else 0 end
                            else 1 end
                        and 1 = case when array_length(company_ids,1) >= 1 then
                            case when layer.company_id = ANY(company_ids) then 1 else 0 end
                            else 1 end
                        and prod.active = True and tmpl.active = True
                        group by layer.company_id, cmp.name, layer.create_date, layer.product_id, prod.default_code, tmpl.name, tmpl.categ_id, cat.complete_name

                )all_d
                group by all_d.company_id, all_d.company_name, all_d.move_date, all_d.product_id, all_d.product_code, all_d.category_id, all_d.category_name)l
        order by l.company_id,l.row_id,l.product_id;

        Insert into final_stock_age_table
        with all_data as (
            Select st.company_id, st.company_name, st.product_id, st.product_name, st.product_category_id, st.category_name,
                sum(st.current_stock) as total_stock, sum(st.current_stock_value) as total_stock_value
            from stock_age_table st
            group by st.company_id, st.company_name, st.product_id, st.product_name, st.product_category_id, st.category_name
        ),
        company_wise_stock_age_table as(
            Select sat.company_id, sum(sat.current_stock) as total_stock_qty, sum(sat.current_stock_value) as total_stock_value
            from stock_age_table sat
            group by sat.company_id
        ),
        oldest_stock_data as (
            Select st.company_id, st.product_id, st.in_date, CASE when st.current_stock < 0 then 0 else st.current_stock end as current_stock,
            CASE when st.current_stock_value < 0 then 0 else st.current_stock_value end as current_stock_value,
                CASE when st.current_stock <= 0 then 0 else (now()::date - st.in_date) end as days_old
            from stock_age_table st
            where row_id = 1
        )

        Select
            all_data.*, oldest.in_date, oldest.days_old, oldest.current_stock, oldest.current_stock_value,
            case when cmp_age.total_stock_qty <= 0.00 then 0 else
                Round(all_data.total_stock / cmp_age.total_stock_qty * 100,3)
            end as stock_qty_ratio,
            case when cmp_age.total_stock_value <= 0.00 then 0 else
                Round(all_data.total_stock_value / cmp_age.total_stock_value * 100,4)
            end as stock_value_ratio
        From
            all_data
                Inner Join oldest_stock_data oldest on oldest.company_id = all_data.company_id and all_data.product_id = oldest.product_id
                Inner Join company_wise_stock_age_table cmp_age on cmp_age.company_id = all_data.company_id;

	    update final_stock_age_table set in_date = null, days_old=0, current_stock=0, current_stock_value=0,
        stock_qty_ratio=0, stock_value_ratio=0 where total_stock <=0;

        update final_stock_age_table sat set current_stock = ly.stock_qty,
                                             current_stock_value = ly.stock_value,
                                             days_old = ly.days_old from
            (
				select lp.* from (
            select
                row_number() over(partition by remaining.company_id, remaining.product_id order by remaining.company_id, remaining.product_id, remaining.move_date) row_id,
                remaining.product_id, remaining.company_id,EXTRACT (DAY from now()::date - remaining.move_date)::numeric as days_old,sum(stock_qty) as stock_qty, sum(stock_value) as stock_value

            from
                (
                select
                    layer.product_id,
                    layer.company_id,
                    layer.remaining_qty as stock_qty,
                    layer.remaining_value as stock_value,
                    case when move.date is null then layer.create_date else move.date end as move_date
                from stock_valuation_layer layer
                        left join stock_move move on layer.stock_move_id = move.id
                        Inner Join product_product prod on prod.id = layer.product_id
                        Inner Join product_template tmpl on tmpl.id = prod.product_tmpl_id

                where layer.remaining_qty > 0
                and prod.active = True and tmpl.active = True
                )remaining
                group by remaining.company_id, remaining.move_date, remaining.product_id)lp
				where lp.row_id=1
                )ly
        where ly.product_id = sat.product_id and ly.company_id = sat.company_id;

        update final_stock_age_table sat set current_stock = 0,
                                             current_stock_value = 0,
                                             days_old = 0 from
            (select cc.category_id,cc.company_id from LATERAL get_category_company_dependent() as cc where cc.cost_method = 'standard')ly


        where ly.category_id = sat.product_category_id and ly.company_id = sat.company_id;

        Return Query
        select
            fs.company_id, fs.company_name, fs.product_id, fs.product_name,
            fs.product_category_id, fs.category_name, fs.total_stock,
            fs.total_stock_value, fs.in_date, fs.days_old, fs.current_stock as oldest_stock_qty,
            fs.current_stock_value as oldest_stock_value, fs.stock_qty_ratio, fs.stock_value_ratio
        from final_stock_age_table fs;
    END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
