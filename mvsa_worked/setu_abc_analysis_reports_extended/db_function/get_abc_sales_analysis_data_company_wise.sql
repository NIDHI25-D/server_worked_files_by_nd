DROP FUNCTION IF EXISTS public.get_abc_sales_analysis_data_company_wise(integer[], integer[], integer[], integer[], date, date, text);

CREATE OR REPLACE FUNCTION public.get_abc_sales_analysis_data_company_wise(
IN company_ids integer[],
IN product_ids integer[],
IN category_ids integer[],
IN warehouse_ids integer[],
IN start_date date,
IN end_date date,
IN abc_analysis_type text)
RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, sales_qty numeric, sales_amount numeric, sales_amount_per numeric, cum_sales_amount_per numeric, analysis_category text) AS
$BODY$
    BEGIN
        Return Query

        with all_data as (
            Select DD.company_id, DD.company_name, DD.product_id, DD.product_name, DD.product_category_id, DD.category_name, sum(DD.sales_qty) as sales_qty, sum(DD.sales_amount) as sales_amount from
                        (
            Select * from get_sales_data(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date)
            )DD
            group by DD.company_id, DD.company_name, DD.product_id, DD.product_name, DD.product_category_id, DD.category_name
        ),
        company_wise_abc_analysis as(
            Select a.company_id, a.company_name, sum(a.sales_qty) as total_sales, sum(a.sales_amount) as total_sales_amount
            from all_data a
            group by a.company_id, a.company_name
        )

        Select final_data.* from
        (
            Select
                result.*,
                case
                    when result.cum_sales_amount_per < 80 then 'A'
                    when result.cum_sales_amount_per >= 80 and result.cum_sales_amount_per <= 95 then 'B'
                    when result.cum_sales_amount_per > 95 then 'C'
                end as analysis_category
            from
            (
                Select
                    *,
                    sum(cum_data.sales_amount_per)
        over (partition by cum_data.company_id order by cum_data.company_id, cum_data.sales_amount_per desc rows between unbounded preceding and current row) as cum_sales_amount_per
                from
                (
                    Select
                        all_data.*,
                        case when wwabc.total_sales_amount <= 0.00 then 0 else
                            Round((all_data.sales_amount / wwabc.total_sales_amount * 100.0)::numeric,2)
                        end as sales_amount_per
                    from all_data
                        Inner Join company_wise_abc_analysis wwabc on all_data.company_id = wwabc.company_id
                    order by sales_amount_per desc
                )cum_data
            )result
        )final_data
        where
        1 = case when abc_analysis_type = 'all' then 1
        else
            case when abc_analysis_type = 'high_sales' then
                case when final_data.analysis_category = 'A' then 1 else 0 end
            else
                case when abc_analysis_type = 'medium_sales' then
                    case when final_data.analysis_category = 'B' then 1 else 0 end
                else
                    case when abc_analysis_type = 'low_sales' then
                        case when final_data.analysis_category = 'C' then 1 else 0 end
                    else 0 end

                end
            end
        end;

    END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;