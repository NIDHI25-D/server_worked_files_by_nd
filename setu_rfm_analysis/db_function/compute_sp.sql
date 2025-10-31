DROP FUNCTION IF EXISTS public.compute_rfm_sp(integer, integer, integer[]);
CREATE OR REPLACE FUNCTION public.compute_rfm_sp(
    IN active_company_id integer,
    IN current_team_id integer,
    IN segment_ids integer[]
)
RETURNS TABLE(
    segment_id integer,
    revenue_ratio double precision,
    sales_ratio double precision,
    partner_ratio double precision,
    team_revenue_ratio double precision,
    team_sales_ratio double precision,
    partners double precision,
    company_wise_sales double precision,
    sales_team_wise_sales double precision,
    company_wise_revenue double precision,
    sales_team_wise_revenue double precision,
    team_partners numeric,
    team_partners_ratio numeric
) AS
$BODY$
DECLARE
    total_customers_company double precision := (SELECT total_customers FROM overall_company_customer_data(active_company_id))::double precision;
    total_revenue_company double precision := (SELECT total_revenue FROM overall_company_data(active_company_id))::double precision;
    total_orders_company double precision := (SELECT total_orders FROM overall_company_data(active_company_id))::double precision;
    total_revenue_sales_team double precision := (SELECT total_revenue FROM overall_team_data(current_team_id))::double precision;
    total_orders_sales_team bigint := (SELECT total_orders FROM overall_team_data(current_team_id))::bigint;
BEGIN
RETURN QUERY
SELECT
    data.id AS segment_id,
    CASE WHEN total_revenue_company > 0 THEN
        ROUND((100 * MAX(data.company_wise_revenue)::float / total_revenue_company))::double precision
    ELSE 0::double precision END AS revenue_ratio,

    CASE WHEN total_orders_company > 0 THEN
        ROUND((100 * MAX(data.company_wise_sales)::float / total_orders_company))::double precision
    ELSE 0::double precision END AS sales_ratio,

    CASE WHEN total_customers_company > 0 THEN
        ROUND((100 * MAX(data.partners)::float / total_customers_company))::double precision
    ELSE 0::double precision END AS partner_ratio,

    CASE WHEN total_revenue_sales_team > 0 THEN
        ROUND((100 * MAX(data.sales_team_wise_revenue)::float / total_revenue_sales_team))::double precision
    ELSE 0::double precision END AS team_revenue_ratio,

    CASE WHEN total_orders_sales_team > 0 THEN
        ROUND((100 * MAX(data.sales_team_wise_sales)::float / total_orders_sales_team))::double precision
    ELSE 0::double precision END AS team_sales_ratio,

    MAX(data.partners)::double precision AS partners,
    MAX(data.company_wise_sales)::double precision AS company_wise_sales,
    MAX(data.sales_team_wise_sales)::double precision AS sales_team_wise_sales,
    MAX(data.company_wise_revenue)::double precision AS company_wise_revenue,
    MAX(data.sales_team_wise_revenue)::double precision AS sales_team_wise_revenue,
    max(data.team_partners) as team_partners,
    max(data.team_partners_ratio) as team_partners_ratio

FROM (
    select
		s.id,
		s.partners as partners,
		0 as company_wise_sales,
		0 as sales_team_wise_sales,
		0 as company_wise_revenue,
		0 as sales_team_wise_revenue,
		sum(s.partners) over()::numeric as team_partners,
		round((s.partners / case when (sum(s.partners) over()) > 0 then (sum(s.partners) over()) else 1 end)::numeric*100) as team_partners_ratio
		from
		(
        select
            srs.id,
            count(ps.partner_id) as partners,
            0 as company_wise_sales,
            0 as sales_team_wise_sales,
            0 as company_wise_revenue,
            0 as sales_team_wise_revenue,
            sum(distinct ps.partner_id) as team_partners
    --		0 as company_wise_pos,
    --		0 as sales_team_wise_pos,
    --		0 as company_wise_pos_revenue,
    --		0 as sales_team_wise_pos_revenue


        from
        setu_rfm_segment srs
        left join partner_segments ps on srs.id = ps.segment_id
        where srs.is_template = false and srs.id = any(segment_ids)
        group by srs.id
        )s

    UNION ALL

    SELECT
        srs.id,
        (
            SELECT
                COUNT(*)
            FROM
                res_partner
            WHERE
                jsonb_pretty(rfm_segment_id ->active_company_id::text)::integer = srs.id
        ) AS partners,
        0 AS company_wise_sales,
        0 AS sales_team_wise_sales,
        0 AS company_wise_revenue,
        0 AS sales_team_wise_revenue,
        0 as team_partners,
		0 as team_partners_ratio
    FROM
        setu_rfm_segment srs
    WHERE
        srs.is_template = true and srs.id = ANY(segment_ids)
    GROUP BY srs.id

    UNION ALL

--        Company wise sales and revenue
   SELECT
        srs.id,
        0 AS partners,
        COUNT(so.id) AS company_wise_sales,
        0 AS sales_team_wise_sales,
        COALESCE(SUM(so.amount_total),0) AS company_wise_revenue,
        0 AS sales_team_wise_revenue,
        0 as team_partners,
		0 as team_partners_ratio
    FROM
        setu_rfm_segment srs
    LEFT JOIN sale_order so ON so.rfm_segment_id = srs.id AND so.company_id = 1
    WHERE srs.id = ANY(segment_ids)
    GROUP BY srs.id

    UNION ALL

--        Sales Team wise sales and revenue
    SELECT
        srs.id,
        0 AS partners,
        0 AS company_wise_sales,
        COUNT(so2.id) AS sales_team_wise_sales,
        0 AS company_wise_revenue,
        COALESCE(SUM(so2.amount_total), 0) AS sales_team_wise_revenue,
		0 as team_partners,
		0 as team_partners_ratio
    FROM
        setu_rfm_segment srs
    LEFT JOIN sale_order so2 ON so2.rfm_team_segment_id = srs.id
    WHERE srs.id = ANY(segment_ids)
    GROUP BY srs.id
)data
GROUP BY data.id;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;









