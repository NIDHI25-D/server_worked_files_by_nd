DROP FUNCTION IF EXISTS public.set_rfm_segment_values_company(integer[], date, character varying);

CREATE OR REPLACE FUNCTION public.set_rfm_segment_values_company(
    company_ids integer[],
    end_date date,
    calculation_type character varying)
RETURNS void AS
$BODY$
BEGIN
    UPDATE sale_order
    SET rfm_segment_id = NULL
    WHERE rfm_segment_id IS NOT NULL;

    UPDATE sale_order so
    SET rfm_segment_id = segment.rfm_segment_id
    FROM (
        SELECT unnest(sale_ids) AS sale_id, rfm_segment_id
        FROM rfm_analysis
    ) AS segment
    WHERE segment.sale_id = so.id;

    IF (SELECT state FROM ir_module_module WHERE name = 'setu_rfm_analysis_extended') = 'installed' THEN
        UPDATE pos_order
        SET rfm_segment_id = NULL
        WHERE rfm_segment_id IS NOT NULL;

        UPDATE pos_order po
        SET rfm_segment_id = pos_segment.rfm_segment_id
        FROM (
            SELECT unnest(pos_ids) AS pos_id, rfm_segment_id
            FROM rfm_analysis
        ) AS pos_segment
        WHERE pos_segment.pos_id = po.id;
    END IF;

    UPDATE res_partner SET rfm_segment_id = NULL;

    UPDATE res_partner rp
		SET rfm_segment_id = jsonb(woo.partner_wise_segment)
	FROM
		(
			SELECT
				foo.partner_id as partner_id,
				CONCAT('{',STRING_AGG(foo.partner_wise_segment, ', '), '}') AS partner_wise_segment
			FROM (
				SELECT
					customer_id AS partner_id,
					company_id,
					rfm_segment_id,
					CONCAT('"', company_id, '":', rfm_segment_id) AS partner_wise_segment
				FROM rfm_analysis
				WHERE company_id = ANY(company_ids)
			) foo
			GROUP BY foo.partner_id
			) woo
		WHERE
		rp.id = woo.partner_id;

    IF calculation_type = 'static' THEN
        update res_partner rp set rfm_segment_id =
                jsonb_set(
                    COALESCE(rp.rfm_segment_id, '{}'),            -- Use an empty JSON object if rfm_segment_id is NULL
                    ('{' || cw_data.company_id || '}')::text[],   -- Dynamic key (company_id)
                    to_jsonb(cw_data.rfm_segment_id),             -- Dynamic value (rfm_segment_id)
                    true                                          -- Create the key if it doesn't exist
                )
            FROM
                (
                SELECT
                    customer_id as partner_id,
                    company_id,
                    rfm_segment_id
                FROM rfm_analysis
                WHERE company_id = ANY(company_ids)
                )cw_data
             WHERE
                rp.id = cw_data.partner_id;
    END IF;

    INSERT INTO rfm_partner_history (partner_id, company_id, current_segment, previous_segment, date_changed)
    SELECT
        current_seg.partner_id,
        current_seg.company_id,
        current_seg.segment_id,
        (SELECT previous_seg.current_segment
         FROM rfm_partner_history previous_seg
         WHERE previous_seg.partner_id = current_seg.partner_id
           AND previous_seg.company_id = current_seg.company_id
         ORDER BY previous_seg.date_changed DESC
         LIMIT 1) AS previous_segment,
        NOW() AS date_changed
    FROM (
        SELECT
            customer_id AS partner_id,
            company_id,
            rfm_segment_id AS segment_id
        FROM rfm_analysis
        WHERE company_id = ANY(company_ids) AND row_num = 1
    ) AS current_seg
    WHERE current_seg.segment_id != COALESCE((SELECT previous_seg.current_segment
                                               FROM rfm_partner_history previous_seg
                                               WHERE previous_seg.partner_id = current_seg.partner_id
                                                 AND previous_seg.company_id = current_seg.company_id
                                               ORDER BY previous_seg.date_changed DESC
                                               LIMIT 1), 0);
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;


