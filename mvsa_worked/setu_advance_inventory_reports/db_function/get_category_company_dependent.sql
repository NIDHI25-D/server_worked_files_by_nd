DROP FUNCTION IF EXISTS get_category_company_dependent();
CREATE OR REPLACE FUNCTION public.get_category_company_dependent()
RETURNS TABLE(
    category_id integer,
    cost_method text,
    property_id integer,
    company_id integer
) AS
$BODY$
BEGIN
    Return Query
    WITH property_methods AS (
    SELECT
        cat.id AS category_id,
        (j.key)::int AS property_id,
        CASE
            WHEN j.value IN ('fifo', 'average') THEN j.value
            ELSE 'standard'
        END AS cost_method
    FROM
        product_category AS cat
    JOIN
        LATERAL jsonb_each_text(cat.property_cost_method) AS j ON true
    ),
    all_companies AS (
        SELECT
            comp.id AS company_id
        FROM
            res_company AS comp
    ),
    all_categories AS (
        SELECT
            DISTINCT id AS category_id
        FROM
            product_category
    )
    SELECT
         cat.category_id,
         COALESCE(pm.cost_method, 'standard') AS cost_method,
         COALESCE(pm.property_id, c.company_id) AS property_id,
         c.company_id
    FROM
        all_companies c
    CROSS JOIN
        all_categories cat
    LEFT JOIN
        property_methods pm ON pm.category_id = cat.category_id AND pm.property_id = c.company_id
    ORDER BY c.company_id, cat.category_id, property_id;

END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
