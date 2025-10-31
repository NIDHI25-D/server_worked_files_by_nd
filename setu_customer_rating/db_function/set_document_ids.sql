--DROP FUNCTION get_sale_ids();
CREATE OR REPLACE FUNCTION public.set_document_ids(
    IN date_limit date,
    IN invoice_due_date_limit date,
    IN grace_days_to_paid_invoice INTEGER,
    IN partner_ids int[] DEFAULT NULL  --MOD (new param)

)
RETURNS void AS
$BODY$
BEGIN

delete from average_sale_rel ar
USING customer_score cs
WHERE ar.score_id = cs.id
  AND cs.partner_id = ANY(partner_ids); --MOD;
insert into average_sale_rel(score_id,sale_id)

(select id as score_id,unnest(cus_score_data.sale_ids) from customer_score as cs
inner join (Select
	    so.partner_id,
	    so.company_id,
	    array_agg(distinct so.id) as sale_ids
	From sale_order so
	inner join sale_order_line sol on sol.order_id = so.id
    inner join sale_order_line_invoice_rel rel on rel.order_line_id = sol.id
    inner join account_move_line aml on aml.id = rel.invoice_line_id
    inner join account_move am on am.id = aml.move_id and am.payment_state in ('paid','in_payment','reversed','partial')
	where so.partner_id = ANY(partner_ids) and so.date_order >= date_limit and
	so.state in ('sale','done') GROUP BY so.partner_id,so.company_id)cus_score_data
on cs.partner_id = cus_score_data.partner_id and cs.company_id = cus_score_data.company_id
WHERE cs.partner_id = ANY(partner_ids)); --MOD

delete from average_pos_sale_rel apr
USING customer_score cs
WHERE apr.score_id = cs.id
  AND cs.partner_id = ANY(partner_ids); --MOD;
insert into average_pos_sale_rel(pos_order_id,score_id)
(select distinct pos_order_id,score_id from
(select id as score_id,unnest(cus_score_data.pos_ids)as pos_order_id from customer_score as cs
inner join (Select
	    po.partner_id,po.company_id,
	    array_agg(distinct po.id) as pos_ids
	From pos_order po
	inner join account_move am on po.account_move = am.id and am.payment_state in ('paid','in_payment','reversed','partial')
--	inner join stock_picking sp on sp.pos_order_id = po.id
--	inner join stock_location sl on sl.id = sp.location_id
	where po.partner_id = ANY(partner_ids) and po.date_order >= date_limit and
	po.state in ('invoiced','paid','done') and (select count(id) from pos_order_line pol where order_id = po.id and pol.qty < 0) = 0
--	and sl.usage = 'internal'
	GROUP BY po.partner_id,po.company_id)cus_score_data
on cs.partner_id = cus_score_data.partner_id and cs.company_id = cus_score_data.company_id
WHERE cs.partner_id = ANY(partner_ids) --MOD
)as main_d);



delete from customer_score_unpaid_after_60_days_invoice_rel rel
    USING customer_score cs
    WHERE rel.score_id = cs.id
    AND cs.partner_id = ANY(partner_ids); --MOD
insert into customer_score_unpaid_after_60_days_invoice_rel(invoice_id,score_id)
(select distinct invoice_id,score_id from
(select id as score_id,unnest(ids) as invoice_id from customer_score as cs
inner join
(select
	ai.partner_id,ai.company_id,
	array_agg(ai.id)as ids
		from account_move as ai
		where
		    ai.partner_id = ANY(partner_ids) and
			ai.payment_state in ('not_paid','partial') and
			ai.invoice_date >= date_limit and ai.state != 'cancel' and
			ai.move_type='out_invoice'
			and invoice_due_date_limit > invoice_date_due and
			ai.invoice_date >= date_limit and ai.l10n_mx_edi_cfdi_uuid is not null
		group by ai.partner_id,ai.company_id)due_after_days on due_after_days.partner_id = cs.partner_id and cs.company_id = due_after_days.company_id
		WHERE cs.partner_id = ANY(partner_ids))as main_dd); --MOD

delete from customer_score_refund_invoice_rel rel
USING customer_score cs
WHERE rel.score_id = cs.id
  AND cs.partner_id = ANY(partner_ids); --MOD
insert into customer_score_refund_invoice_rel(score_id,invoice_id)
(select id as score_id,unnest(ids)as id from customer_score as cs
inner join
(select distinct ai.partner_id,ai.company_id,
	array_agg(distinct ai.id) as ids
	from account_move as ai
		--inner join account_move as air on air.id = ai.reversed_entry_id or ai.reversed_entry_id is null
		inner join account_move_line as ail on ail.move_id = ai.id
		inner join sale_order_line_invoice_rel as rel on ail.id = rel.invoice_line_id
		inner join sale_order_line as sol on rel.order_line_id = sol.id
		inner join sale_order as so on sol.order_id = so.id
			where
    			ai.partner_id = ANY(partner_ids) and
				ai.payment_state in ('paid','in_payment','reversed','partial','not_paid')
 and
				ai.move_type = 'out_refund' and ai.state != 'cancel'
				and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',ai.company_id)),']') in ('[]') and
						 	ai.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',ai.company_id)),']') not in ('[]')
						  and ai.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',ai.company_id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end and
				so.state in ('sale','done') and
				ai.invoice_date >= date_limit
				GROUP BY ai.partner_id,ai.company_id,ai.id)credit_notes on credit_notes.partner_id = cs.partner_id and credit_notes.company_id = cs.company_id
				WHERE partner_ids IS NULL OR cs.partner_id = ANY(partner_ids)); --MOD

delete from customer_score_paid_after_due_invoice_rel rel
    USING customer_score cs
    WHERE rel.score_id = cs.id
    AND cs.partner_id = ANY(partner_ids); --MOD
insert into customer_score_paid_after_due_invoice_rel (score_id,invoice_id)
(select id as score_id,unnest(invoice_done_after_due) from customer_score cs
inner join (select vals.partner_id,vals.company_id,
       array_agg(id) as invoice_done_after_due From
                   (select
                        ai.partner_id,
                        ai.company_id,
                        ai.id,
                        ai.amount_total

					from account_move as ai
						where
						    ai.partner_id = ANY(partner_ids)
							and ai.payment_state in ('paid','in_payment','reversed')
							and ai.move_type='out_invoice'
							and ai.invoice_date >= date_limit
							and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',ai.company_id)),']') in ('[]') and
						 	ai.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',ai.company_id)),']') not in ('[]')
						  and ai.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',ai.company_id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
							and (select invoice_date_due from account_move where id = ai.id)::date + grace_days_to_paid_invoice
							     <
							    (SELECT
								 					max(date)
								 				from
												(SELECT
                                                    max(move.date) as date
                                                --FROM account_payment payment
                                                FROM account_move move
                                                 --ON move.id = payment.move_id
                                                JOIN account_move_line line ON line.move_id = move.id
                                                JOIN account_partial_reconcile part ON
                                                    part.debit_move_id = line.id
                                                    OR
                                                    part.credit_move_id = line.id
                                                JOIN account_move_line counterpart_line ON
                                                    part.debit_move_id = counterpart_line.id
                                                    OR
                                                    part.credit_move_id = counterpart_line.id
                                                JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                                                JOIN account_account account ON account.id = line.account_id
                                                WHERE account.account_type IN ('asset_receivable', 'liability_payable')
                                                    --AND payment.id IN %(payment_ids)s
                                            AND invoice.id in (ai.id)
                                                    AND line.id != counterpart_line.id
                                                    AND invoice.move_type in ('out_invoice')
                                                GROUP BY move.date)as dates)::date

				group by ai.partner_id,ai.id,ai.company_id

			)as vals group by vals.partner_id,vals.company_id)invoice_data on invoice_data.partner_id = cs  .partner_id and invoice_data.company_id = cs.company_id
			WHERE cs.partner_id = ANY(partner_ids)); --MOD


insert into customer_score_refund_invoice_rel(score_id,invoice_id)
(select id as score_id,unnest(ids)as id from customer_score as cs
inner join
(select distinct air.partner_id,air.company_id,
	array_agg(distinct air.id) as ids
	from pos_order as po
	    inner join account_move am on am.id = po.account_move
		right join account_move as air on air.reversed_entry_id = am.id
			where
			    air.partner_id = ANY(partner_ids) and
				air.payment_state in ('paid','in_payment','reversed','partial','not_paid') and
				air.move_type = 'out_refund' and
				po.state in ('paid','invoiced','done') and air.state != 'cancel'
				and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']') in ('[]') and
						 	air.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']') not in ('[]')
						  and air.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end and
				air.invoice_date >= date_limit
				GROUP BY air.partner_id,air.company_id,air.id)credit_notes on credit_notes.partner_id = cs.partner_id and credit_notes.company_id = cs.company_id
				WHERE cs.partner_id = ANY(partner_ids)); --MOD

insert into customer_score_refund_invoice_rel(score_id,invoice_id)
(select id as score_id,unnest(ids)as id from customer_score as cs
inner join
(select distinct am.partner_id,am.company_id,
	array_agg(distinct am.id) as ids
	from pos_order as po
	    inner join account_move am on am.id = po.account_move

			where
			    am.partner_id = ANY(partner_ids) and
				am.payment_state in ('paid','in_payment','reversed','partial','not_paid') and
				am.move_type = 'out_refund' and
				po.state in ('paid','invoiced','done') and am.state != 'cancel' and
				am.invoice_date >= date_limit
				and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']') in ('[]') and
						 	am.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']') not in ('[]')
						  and am.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',po.company_id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
 				and am.id not in (select invoice_id from customer_score_refund_invoice_rel)
				GROUP BY am.partner_id,am.company_id,am.id)credit_notes on credit_notes.partner_id = cs.partner_id and credit_notes.company_id = cs.company_id
				WHERE cs.partner_id = ANY(partner_ids)); --MOD

delete from customer_score_invoice_rel csr
    WHERE csr.score_id IN (
    SELECT cs.id FROM customer_score cs
    WHERE cs.partner_id = ANY(partner_ids)
);
insert into customer_score_invoice_rel(score_id,invoice_id)
(select id as score_id,unnest(ids)as id from customer_score as cs
inner join
(select
	am.partner_id,
	am.company_id ,
	array_agg(distinct am.id) as ids

from
	account_move am
	join account_move_line aml on aml.move_id = am.id
where
    am.partner_id = ANY(partner_ids) and
	am.move_type = 'out_invoice' and am.state not in ('cancel','draft') and
        am.invoice_date >= date_limit
        and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',am.company_id)),']') in ('[]') and
						 	am.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',am.company_id)),']') not in ('[]')
						  and am.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',am.company_id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
        and am.payment_state in ('paid','in_payment','reversed','partial','not_paid')
        and aml.product_id not in (select value::int from ir_config_parameter  where key = 'sale.default_deposit_product_id')
GROUP BY am.partner_id,am.company_id)invoices on invoices.partner_id = cs.partner_id and invoices.company_id = cs.company_id
WHERE cs.partner_id = ANY(partner_ids)) --MOD

;


END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

