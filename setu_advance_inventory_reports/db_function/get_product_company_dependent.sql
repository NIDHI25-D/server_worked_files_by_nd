DROP FUNCTION IF EXISTS get_product_company_dependent();
CREATE OR REPLACE FUNCTION public.get_product_company_dependent()
RETURNS TABLE(
    product_id integer,
    cost_price float,
    property_id integer,
    company_id integer
) AS
$BODY$
BEGIN
    Return Query
    WITH property_methods AS (
    SELECT
        prod.id AS product_id,
        (j.key)::int AS property_id,
        CASE
            WHEN NULLIF((j.value)::float, 0) IS NOT NULL AND (j.value)::float > 0 THEN (j.value)::float
            ELSE 0
        END AS cost_price
    FROM
        product_product AS prod
    JOIN
        LATERAL jsonb_each_text(prod.standard_price) AS j ON true
),
all_companies AS (
    SELECT
        comp.id AS company_id
    FROM
        res_company AS comp
),
all_products AS (
    SELECT
        DISTINCT id AS product_id
    FROM
        product_product
)
SELECT
     prod.product_id,
     COALESCE(pm.cost_price, 0) AS cost_price,
     COALESCE(pm.property_id, c.company_id) AS property_id,
     c.company_id
FROM
    all_companies c
CROSS JOIN
    all_products prod
LEFT JOIN
    property_methods pm ON pm.product_id = prod.product_id AND pm.property_id = c.company_id

ORDER BY c.company_id, prod.product_id, property_id;

END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100
ROWS 1000;
