DROP FUNCTION IF EXISTS public.get_sales_data_for_rfm(integer[], date, date, character varying);
CREATE OR REPLACE FUNCTION public.get_sales_data_for_rfm(
    IN company_ids integer[],
    IN start_date date,
    IN end_date date,
    IN segment_type character varying)
RETURNS void AS
$BODY$

BEGIN

    IF (SELECT state FROM ir_module_module WHERE name = 'setu_rfm_analysis_extended') = 'installed' THEN
        PERFORM gather_sales_and_pos_data(company_ids, start_date, end_date);
    ELSE
        PERFORM gather_sales_data(company_ids, start_date, end_date);
    END IF;

    DROP TABLE IF EXISTS rfm_transaction_table;
    CREATE TEMPORARY TABLE rfm_transaction_table(
        company_id integer,
        customer_id integer,
        total_orders integer,
        total_order_value numeric,
        days_from_last_purchase integer,
        sale_ids integer[],
        pos_ids integer[]
    );

    INSERT INTO rfm_transaction_table
    SELECT
        sales.company_id,
        sales.partner_id,
        COUNT(sales.so_id) + COUNT(sales.pos_id) AS total_orders,
        SUM(COALESCE(sales.amount_total_per_line, 0) + COALESCE(sales.tax_amount, 0)) AS total_order_value,
        DATE_PART('day', NOW()::timestamp - MAX(sales.date_order)::timestamp) AS days_from_last_purchase,
        ARRAY_AGG(sales.so_id) AS sale_ids,
        ARRAY_AGG(sales.pos_id) AS pos_ids
    FROM sales_data sales
    GROUP BY sales.partner_id, sales.company_id;

    IF segment_type = 'sales_team' THEN
        DROP TABLE IF EXISTS rfm_transaction_table_team;
        CREATE TEMPORARY TABLE rfm_transaction_table_team(
            team_id integer,
            customer_id integer,
            total_orders integer,
            total_order_value numeric,
            days_from_last_purchase integer,
            sale_ids integer[],
            pos_ids integer[]
        );

        INSERT INTO rfm_transaction_table_team
        SELECT
            sales.team_id,
            sales.partner_id,
            COUNT(sales.so_id) + COUNT(sales.pos_id) AS total_orders,
            SUM(COALESCE(sales.amount_total_per_line, 0) + COALESCE(sales.tax_amount, 0)) AS total_order_value,
            DATE_PART('day', NOW()::timestamp - MAX(sales.date_order)::timestamp) AS days_from_last_purchase,
            ARRAY_AGG(sales.so_id) AS sale_ids,
            ARRAY_AGG(sales.pos_id) AS pos_ids
        FROM sales_data sales
        GROUP BY sales.partner_id, sales.team_id;
    END IF;

END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
