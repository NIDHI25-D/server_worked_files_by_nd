--DROP FUNCTION get_invoice_due_after_x_days_ids();
CREATE OR REPLACE FUNCTION public.create_customer_score_records(partner_ids integer[])
RETURNS void AS
$BODY$
BEGIN
--CREATE TABLE IF NOT EXISTS score_to_create (
--                            partner_id integer PRIMARY KEY);
--
--DELETE FROM score_to_create;
--delete from customer_score; --This part is commented as it used to take much time and added uper given query
DELETE FROM customer_score cs
    USING res_partner rp
    WHERE cs.partner_id = rp.id
    AND rp.customer_rank > 0
    AND rp.active = TRUE
    AND rp.id = ANY (partner_ids);
INSERT INTO customer_score(partner_id,company_id)

SELECT rp.id AS partner_id, sc.company_id
    FROM res_partner rp
    CROSS JOIN (SELECT DISTINCT company_id FROM score_conf) sc
    WHERE NOT EXISTS (
          SELECT 1
          FROM customer_score cs
          WHERE cs.partner_id = rp.id
            AND cs.company_id = sc.company_id
      )
      and rp.active = true and rp.customer_rank > 0 and rp.id = ANY (partner_ids);

--This part is commented as it used to take much time and added uper given query
--select * from
--(SELECT id,unnest((select array_agg(distinct company_id) from score_conf))as company_id FROM res_partner)as partners
--where (partners.id,partners.company_id) not in (select partner_id,company_id from customer_score);

END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
