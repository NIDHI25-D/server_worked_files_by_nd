DROP FUNCTION IF EXISTS public.overall_company_customer_data(integer);
CREATE OR REPLACE FUNCTION public.overall_company_customer_data(IN active_company_id integer)
RETURNS TABLE(
    total_customers bigint
) AS
$BODY$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_customers
    FROM
        res_partner rp
    WHERE
        rp.rfm_segment_id IS NOT NULL
        and (select jsonb_object_keys(rfm_segment_id::jsonb)::integer) = active_company_id;
--        AND
--        (active_company_id) in (select distinct id from res_company);
--        active_company_id in (select distinct id from res_company
--        select array_agg(distinct id) from res_company where id = active_company_id));
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;


