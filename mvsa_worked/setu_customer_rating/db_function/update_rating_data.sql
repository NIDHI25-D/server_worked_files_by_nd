--DROP FUNCTION get_pre_order_ids();
CREATE OR REPLACE FUNCTION public.update_rating_data(
IN partner_ids int[] DEFAULT NULL --MOD: Added optional partner_ids filter
)
RETURNS void AS
$BODY$
BEGIN
update customer_score as cs
       set partner_rating =
       (select id from customer_rating as cr
        where cs.total_score <= cr.to_score and
        cs.total_score >= cr.from_score and cs.company_id = cr.company_id)
        WHERE partner_ids IS NULL OR cs.partner_id = ANY(partner_ids); --MOD: Only selected partners


--Update customer total score
update res_partner rp
	set total_score = jsonb(foo.partner_wise_total_score)
from (
		select
			customer_ts.partner_id as partner_id,
			unnest((select array_agg(distinct company_id) from score_conf)) as company_id,
			CONCAT('{',STRING_AGG(customer_ts.partner_wise_total_score, ', '), '}') AS partner_wise_total_score
			from (
					select
						id,
						partner_id,
						company_id,
						CONCAT('"', company_id, '":', total_score) AS partner_wise_total_score
					from customer_score cs
					WHERE partner_ids IS NULL OR cs.partner_id = ANY(partner_ids) --MOD
				)customer_ts
				GROUP BY customer_ts.partner_id
		)as foo

where rp.id = foo.partner_id
AND rp.id = ANY(partner_ids); --MOD

--Update customer Rating
update res_partner rp
	set rating = jsonb(foo.partner_wise_rating)
from (
		select
			customer_ts.partner_id as partner_id,
			CONCAT('{',STRING_AGG(customer_ts.partner_wise_rating, ', '), '}') AS partner_wise_rating
			from (
					select
						partner_id,
						company_id,
						partner_rating,
						CONCAT('"', company_id, '":', partner_rating) AS partner_wise_rating
					from customer_score cs
					where partner_rating is not null
					AND cs.partner_id = ANY(partner_ids) --MOD
				)customer_ts
				GROUP BY customer_ts.partner_id
		)as foo
where rp.id = foo.partner_id
AND rp.id = ANY(partner_ids); --MOD

--Update customer customer score
update res_partner rp
	set customer_score_id = jsonb(foo.partner_wise_score)
from (
		select
			customer_ts.partner_id as partner_id,
			CONCAT('{',STRING_AGG(customer_ts.partner_wise_score, ', '), '}') AS partner_wise_score
			from (
					select
						id,
						partner_id,
						company_id,
						CONCAT('"', company_id, '":', id) AS partner_wise_score
					from customer_score cs
				)customer_ts
				GROUP BY customer_ts.partner_id
		)as foo

where rp.id = foo.partner_id
AND rp.id = ANY(partner_ids); --MOD




END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
