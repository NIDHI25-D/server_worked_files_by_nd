DROP FUNCTION IF EXISTS public.set_rfm_segment_values_team(integer[], date, character varying);

CREATE OR REPLACE FUNCTION public.set_rfm_segment_values_team(
    company_ids integer[],
    end_date date,
    calculation_type character varying)
RETURNS void AS
$BODY$
BEGIN

    DELETE FROM partner_segments
    WHERE company_id = ANY(company_ids) OR company_id IS NULL;

    IF calculation_type = 'static' THEN
        INSERT INTO partner_segments(partner_id, segment_id, team_id, score_id)
        SELECT customer_id, rfm_segment_id, team_id, rfm_score_id
        FROM rfm_analysis_team
        WHERE row_num = 1 AND rfm_segment_id IS NOT NULL;
    ELSE
        INSERT INTO partner_segments(partner_id, segment_id, team_id, score_id)
        SELECT customer_id, rfm_segment_id, team_id, NULL AS score_id
        FROM rfm_analysis_team
        WHERE row_num = 1 AND rfm_segment_id IS NOT NULL;
    END IF;

    UPDATE sale_order so
    SET rfm_team_segment_id = NULL
    WHERE rfm_team_segment_id IS NOT NULL;

    UPDATE sale_order so
    SET rfm_team_segment_id = orders.rfm_segment_id
    FROM (
        SELECT unnest(sale_ids) AS sale_id, rfm_segment_id
        FROM rfm_analysis_team
        WHERE row_num = 1 AND rfm_segment_id IS NOT NULL
    ) AS orders
    WHERE orders.sale_id = so.id;

    IF (SELECT state FROM ir_module_module WHERE name = 'setu_rfm_analysis_extended') = 'installed' THEN
        UPDATE pos_order p
        SET rfm_team_segment_id = NULL
        WHERE rfm_team_segment_id IS NOT NULL;

        UPDATE pos_order p
        SET rfm_team_segment_id = pos_orders.rfm_segment_id
        FROM (
            SELECT unnest(pos_ids) AS pos_id, rfm_segment_id
            FROM rfm_analysis_team
            WHERE row_num = 1 AND rfm_segment_id IS NOT NULL
        ) AS pos_orders
        WHERE pos_orders.pos_id = p.id;
    END IF;

    INSERT INTO rfm_partner_team_history(partner_id, team_id, current_segment, previous_segment, date_changed)
    SELECT
        partner_segments.partner_id,
        partner_segments.team_id,
        partner_segments.segment_id,
        (SELECT previous_seg.current_segment
         FROM rfm_partner_team_history previous_seg
         WHERE previous_seg.partner_id = partner_segments.partner_id
           AND previous_seg.team_id = partner_segments.team_id
         ORDER BY previous_seg.date_changed DESC
         LIMIT 1) AS previous_segment,
        NOW() AS date_changed
    FROM (
        SELECT
            customer_id AS partner_id,
            team_id,
            rfm_segment_id AS segment_id
        FROM rfm_analysis_team
        WHERE row_num = 1
    ) AS partner_segments
    WHERE partner_segments.segment_id != COALESCE((SELECT previous_seg.current_segment
                                                    FROM rfm_partner_team_history previous_seg
                                                    WHERE previous_seg.partner_id = partner_segments.partner_id
                                                      AND previous_seg.team_id = partner_segments.team_id
                                                    ORDER BY previous_seg.date_changed DESC
                                                    LIMIT 1), 0);
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
