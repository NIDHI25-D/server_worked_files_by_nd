CREATE OR REPLACE FUNCTION public.set_customer_scores(
    IN date_limit date,
    IN months numeric,
    IN invoice_due_date_limit date,
    IN grace_days_to_paid_invoice INTEGER,
    IN score_conf_avg_sales_amt_id numeric,
    IN score_conf_avg_monthly_sales_refund_id numeric,
    IN score_conf_qty_invoice_paid_after_due_id numeric,
    IN score_conf_amt_invoice_paid_after_due_id numeric,
    IN score_conf_qty_invoice_paid_after_x_days_id numeric,
    IN score_conf_amt_invoices_due_after_x_days_id numeric,
    IN score_conf_avg_payment_days_id numeric,
    IN partner_ids integer[] DEFAULT '{}'
)
RETURNS void AS
$BODY$

BEGIN


update customer_score as cs
set
	avg_monthly_sales_score = cs2.avg_sales_score,
	average_monthly_amount  = cs2.average_monthly_amount,
	average_amount_sales_average = cs2.average_amount_sales_average,
    average_amount_refund_average = cs2.average_amount_refund_average,
    avg_monthly_refund_score = cs2.avg_refund_score,
    qty_invoice_paid_score = cs2.due_date_qty,
    due_qty = cs2.due_qty,
    amount_invoice_paid_score = cs2.due_date_score_amt,
    due_date_amount = cs2.due_date_amount,
    qty_invoices_due_after_60_days_score = cs2.due_after_60_qty,
    due_after_60_quantity = cs2.due_after_60_quantity,
    amount_invoices_due_after_60_days_score = cs2.due_after_60_amt,
    due_after_60_amount = cs2.due_after_60_amount,
    average_payment_days_score = cs2.avg_pay_score,
    avg_pay_days = cs2.avg_pay_days,
    pre_sale_orders_canceled_score = cs2.pre_cancel_score,
    total_score = cs2.total_score,
    company_id = cs2.company_id



from
(

    select
      main_data.partner_id,
      main_data.avg_sales_score,
      main_data.average_monthly_amount,
      main_data.average_amount_sales_average as average_amount_sales_average,
      main_data.average_amount_refund_average as average_amount_refund_average,
      main_data.avg_refund_score,
     -- main_data.sales_average_for_refund_percentage as sales_average_for_refund_percentage,
     -- main_data.refund_average_for_refund_percentage as refund_average_for_refund_percentage,
      main_data.due_date_score_amt,
	  main_data.due_date_amount as due_date_amount,
      main_data.due_date_qty,
	  main_data.due_qty as due_qty,
      main_data.due_after_60_amt,
	  main_data.due_after_60_amount as due_after_60_amount,
      main_data.due_after_60_qty,
	  main_data.due_after_60_quantity as due_after_60_quantity,
      main_data.pre_cancel_score,
      main_data.avg_pay_score,
	  main_data.avg_pay_days as avg_pay_days,
      (
        main_data.avg_sales_score  + main_data.avg_refund_score +  main_data.due_date_score_amt + main_data.due_date_qty + main_data.due_after_60_amt + main_data.due_after_60_qty + main_data.pre_cancel_score + main_data.avg_pay_score
      ) as total_score,
      main_data.company_id
    from
      (
        select
          data.partner_id,
          data.company_id,
          max(data.avg_sales_score) avg_sales_score,
          max(data.average_monthly_amount) as average_monthly_amount,
          max(data.average_amount_sales_average) as average_amount_sales_average,
          max(data.average_amount_refund_average) as average_amount_refund_average,
          max(data.avg_refund_score) avg_refund_score,
         -- max(data.sales_average_for_refund_percentage) as sales_average_for_refund_percentage,
         -- max(data.refund_average_for_refund_percentage) as refund_average_for_refund_percentage,
          max(data.due_date_score_amt) due_date_score_amt,
		  max(data.due_date_amount) as due_date_amount,
          max(data.due_date_qty) due_date_qty,
		  max(data.due_qty) as due_qty,
          max(data.due_after_60_amt) due_after_60_amt,
		  max(data.due_after_60_amount) as due_after_60_amount,
          max(data.due_after_60_qty) due_after_60_qty,
		  max(data.due_after_60_quantity) as due_after_60_quantity,
          max(data.pre_cancel_score) pre_cancel_score,
          max(data.avg_pay_score) avg_pay_score,
		  max(data.avg_pay_days) as avg_pay_days
        from
          (
            --Lines with 0 initially
            select
              id as partner_id,
              company_id as company_id,
              0 as avg_sales_score,
              0 as average_monthly_amount,
              0 as average_amount_sales_average,
              0 as average_amount_refund_average,
              0 as avg_refund_score,
           --   0 as sales_average_for_refund_percentage,
            --  0 as refund_average_for_refund_percentage,
              0 as due_date_score_amt,
			  0 as due_date_amount,
              0 as due_date_qty,
			  0 as due_qty,
              0 as due_after_60_amt,
			  0 as due_after_60_amount,
              0 as due_after_60_qty,
			  0 as due_after_60_quantity,
              0 as pre_cancel_score,
              0 as avg_pay_score,
			  0 as avg_pay_days
            from
              (
                select
                  id,
                  unnest(
                    (
                      select
                        array_agg(companies.id)
                      from
                        (
                          select
                            distinct company_id as id
                          from
                            score_conf
                          order by
                            id
                        ) as companies
                    )
                  ) as company_id
                from
                  res_partner
                  where
                  id = ANY(partner_ids)  --MOD
              ) as partner_data
            UNION
              --Another one
            select
              partner_amount.partner_id as partner_id,
              partner_amount.company_id as company_id,
              (
                select
                  pre_score
                from
                  score_conf_line_price lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'avg_monthly_sales'
                  and sc.company_id = partner_amount.company_id
                  and partner_amount.average_amount >= lin.from_price
                  and partner_amount.average_amount <= lin.to_price
              ) as avg_sales_score,
              partner_amount.average_amount as average_monthly_amount,
              average_amount_sales_average as average_amount_sales_average,
              average_amount_refund_average as average_amount_refund_average,
			   case when partner_amount.refund_percentage = 0 then (
                select
                  max(pre_score)
                from
                  score_conf_line_percentage line
                  inner join score_conf sc on sc.id = line.score_conf_id
                where
                  sc.company_id = partner_amount.company_id
              ) ELSE (
                select
                  pre_score
                from
                  score_conf_line_percentage line
                  inner join score_conf sc on sc.id = line.score_conf_id
                where
                  sc.company_id = partner_amount.company_id
                  and partner_amount.refund_percentage >= from_percentage
                  and partner_amount.refund_percentage <= to_percentage
              ) END avg_refund_score,
              --0 as avg_refund_score,
             -- 0 as sales_average_for_refund_percentage,
            --  0 as refund_average_for_refund_percentage,
              0 as due_date_score_amt,
			  0 as due_date_amount,
              0 as due_date_qty,
			  0 as due_qty,
              0 as due_after_60_amt,
			  0 as due_after_60_amount,
              0 as due_after_60_qty,
			  0 as due_after_60_quantity,
              0 as pre_cancel_score,
              0 as avg_pay_score,
			  0 as avg_pay_days
            from
              (
                Select
                  partner_id,
                  company_id,
                  (sales_average - refund_average)/ months as average_amount,
                  sales_average as average_amount_sales_average,
                  refund_average as average_amount_refund_average,
				  case when sales_average > 0 then round(
                        (refund_average * 100)/ sales_average
                      ) else 100 end as refund_percentage
                From
                  (select
                        sales_and_refund_data.partner_id as partner_id,
                        sales_and_refund_data.company_id as company_id,
                        max(sales_and_refund_data.refund_average) as refund_average,
                        max(sales_and_refund_data.sales_average) as sales_average

                   from
                      (
                        select refund_average_data.partner_id as partner_id,
                               refund_average_data.company_id as company_id,
                               sum(refund_average_data.refund_average) as refund_average,
                               sum(refund_average_data.sales_average) as sales_average
                        from (
                              select
                                  rfi.partner_id as partner_id,
                                  rfi.company_id as company_id,
                                  sum(rfi.refund_average) refund_average,
                                  0 as sales_average
                              from
                                  (select
                                          refund.move_id,
                                          refund.partner_id,
                                          refund.company_id,
                                          max(refund.refund_average) refund_average,
                                          0 as sales_average
                                from
                                  (
                                    ---fix this
                                    select
                                      air.partner_id,
                                      air.company_id,
                                      sum(
                                        case when air.currency_id = com.currency_id then abs(air.amount_untaxed) else round(
                                          (
                                            abs(air.amount_untaxed) / coalesce(
                                              (
                                                select
                                                  rate
                                                from
                                                  get_nearest_currency_rate(
                                                    air.invoice_date :: date, air.company_id
                                                  )
                                                where
                                                  currency_id = air.currency_id
                                              ),
                                              1
                                            )
                                          ),
                                          2
                                        ) end
                                      ) as refund_average,
                                      air.id as move_id
                                    from
                                      pos_order po
                                      inner join account_move am on am.id = po.account_move
                                      right join account_move as air on air.reversed_entry_id = am.id
                                      inner join res_company com on com.id = am.company_id

                                    where air.partner_id = ANY(partner_ids) and
                                      po.state in ('paid', 'invoiced', 'done')
                                      and air.payment_state in (
                                        'paid', 'in_payment', 'reversed',
                                        'partial', 'not_paid'
                                      )
                                      and air.state != 'cancel'
                                      and air.move_type = 'out_refund'
                                      and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']') in ('[]') and
						 	air.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']') not in ('[]')
						  and air.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
                                      and air.state != 'cancel'
                                      and air.invoice_date >= date_limit
                                    GROUP BY
                                      air.partner_id,
                                      air.company_id,
                                      air.id ---fix this
                                    UNION ALL
                                    select
                                      am.partner_id,
                                      am.company_id,
                                      sum(
                                        case when am.currency_id = com.currency_id then abs(am.amount_untaxed) else round(
                                          (
                                            ABS(am.amount_untaxed) / coalesce(
                                              NULLIF(
                                                (
                                                  select
                                                    rate
                                                  from
                                                    get_nearest_currency_rate(
                                                      am.invoice_date :: date, am.company_id
                                                    )
                                                  where
                                                    currency_id = am.currency_id
                                                ),
                                                0
                                              ),
                                              1
                                            )
                                          ),
                                          2
                                        ) end
                                      ) as refund_average,
                                      am.id as move_id
                                    from
                                      pos_order po
                                      inner join account_move am on am.id = po.account_move
                                      inner join res_company com on com.id = am.company_id

                                    where am.partner_id = ANY(partner_ids) and
                                      po.state in ('paid', 'invoiced', 'done')
                                      and am.payment_state in (
                                        'paid', 'in_payment', 'reversed',
                                        'partial', 'not_paid'
                                      )
                                      and am.move_type = 'out_refund'
                                      and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']') in ('[]') and
						 	am.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']') not in ('[]')
						  and am.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.journal_ids_',com.id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
                                      and am.state != 'cancel'
                                      and am.invoice_date >= date_limit
                                    GROUP BY
                                      am.partner_id,
                                      am.company_id,
                                      am.id
                                  ) as refund
                                group by
                                  refund.move_id,
                                  refund.partner_id,
                                  refund.company_id)rfi
                                  group by
                                  rfi.partner_id,
                                  rfi.company_id

                            union all

                            select
                              ram.partner_id as partner_id,
                              ram.company_id as comapny_id,
                              sum(
                                case when ram.currency_id = com.currency_id then abs(ram.amount_untaxed) else --round((ram.amount_total / (select rate from get_nearest_currency_rate(ram.invoice_date::date,ram.company_id) where currency_id = ram.currency_id)),2)
                                round(
                                  abs(ram.amount_untaxed) / coalesce(
                                    (
                                      select
                                        rate
                                      from
                                        get_nearest_currency_rate(
                                          ram.invoice_date :: date, ram.company_id
                                        )
                                      where
                                        currency_id = ram.currency_id
                                    ),
                                    1
                                  ),
                                  2
                                ) end
                              ) as refund_average,
                              0 as sales_average
                            from
                              (
                                select
                                  distinct ai.id
                                from
                                  account_move as ai --inner join account_move as air on air.id = ai.reversed_entry_id  or  ai.reversed_entry_id is null
                                  inner join account_move_line as ail on ail.move_id = ai.id
                                  inner join sale_order_line_invoice_rel as rel on ail.id = rel.invoice_line_id
                                  inner join sale_order_line as sol on rel.order_line_id = sol.id
                                  inner join sale_order as so on sol.order_id = so.id

                                where ai.partner_id = ANY(partner_ids) and
                                  ai.payment_state in (
                                    'paid', 'in_payment', 'reversed',
                                    'partial', 'not_paid'
                                  )
                                  and ai.move_type = 'out_refund'
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
                                      ) then 1 else 0 end end
                                  and so.state in ('sale', 'done')
                                  and ai.state != 'cancel'
                                  and ai.invoice_date >= date_limit
                              ) as ri
                              inner join account_move ram on ram.id = ri.id
                              inner join res_company com on com.id = ram.company_id
                              where ram.partner_id = ANY(partner_ids)
                            group by
                              ram.partner_id,
                              ram.company_id)refund_average_data  group by refund_average_data.partner_id , refund_average_data.company_id

                        union all


                                select invoice_average.partner_id ,
                                       invoice_average.company_id,
                                       0 as refund_average,
                                       sum(invoice_average.sales_average) as sales_average
                                from (
                                      select
                                        distinct am.id as move_id,
                                        am.partner_id as partner_id,
                                        am.company_id as company_id,
                                        am.amount_untaxed_signed as sales_average


                                      from
                                        account_move am
                                        join account_move_line aml on aml.move_id = am.id
                                        inner join res_company com on com.id = am.company_id
                                      where
                                        am.move_type = 'out_invoice' and am.state not in ('cancel','draft') and
                                              am.invoice_date >= date_limit
                                              and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',com.id)),']') in ('[]') and
                                                am.journal_id in (select id from account_journal where active = 't') then 1
                                              else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',com.id)),']') not in ('[]')
                                              and am.journal_id = any(
                                                            string_to_array(
                                                              replace(
                                                                replace(
                                                                  replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.invoice_journal_ids_',com.id)),']'), '[', ''),
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
                                              and am.partner_id = ANY(partner_ids)
                                      GROUP BY am.partner_id,am.company_id,am.id
                                      )invoice_average
                                GROUP BY invoice_average.partner_id,invoice_average.company_id
                )sales_and_refund_data
                where sales_and_refund_data.partner_id = ANY(partner_ids)
                group by sales_and_refund_data.partner_id, sales_and_refund_data.company_id )a
              ) as partner_amount
            UNION
              --Another one
            select
            values
              .partner_id as partner_id,
            values
              .company_id as company_id,
              0 as avg_sales_score,
              0 as average_monthly_amount,
              0 as average_amount_sales_average,
              0 as average_amount_refund_average,
              0 as avg_refund_score,
             -- 0 as sales_average_for_refund_percentage,
             -- 0 as refund_average_for_refund_percentage,
              (
                select
                  pre_score
                from
                  score_conf_line_price lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'amt_invoice_paid'
                  and sc.company_id =
                values
                  .company_id
                  and
                values
                  .amount >= lin.from_price
                  and
                values
                  .amount <= lin.to_price
              ) as due_date_score_amt,
			  values.amount as due_date_amount,
              (
                select
                  pre_score
                from
                  score_conf_line_qty lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'qty_invoice_paid'
                  and sc.company_id =
                values
                  .company_id
                  and
                values
                  .qty >= lin.from_quantity
                  and
                values
                  .qty <= lin.to_quantity
              ) as due_date_qty,
			  values.qty as due_qty,
              0 as due_after_60_amt,
			  0 as due_after_60_amount,
              0 as due_after_60_qty,
			  0 as due_after_60_quantity,
              0 as pre_cancel_score,
              0 as avg_pay_score,
			  0 as avg_pay_days
            from
              (
                select
                  vals.partner_id,
                  vals.company_id,
                  max(vals.amount) as amount,
                  max(vals.qty) as qty
                from
                  (
                    select
                      paid_invoices.partner_id,
                      paid_invoices.company_id,
                      0 as amount,
                      0 as qty
                    From
                      (
                        select
                          ai.partner_id,
                          ai.id,
                          ai.name,
                          ai.company_id,
                          ai.amount_untaxed
                        from
                          account_move as ai
                        where
                          ai.payment_state in ('paid', 'in_payment', 'reversed')
                          and ai.move_type = 'out_invoice'
                          and ai.invoice_date >= date_limit
                          and ai.partner_id = ANY(partner_ids)
                      ) as paid_invoices
                    where
                      (
                        select
                          invoice_date_due
                        from
                          account_move
                        where
                          id = paid_invoices.id
                      ):: date >= (
                        SELECT
                          max(date)
                        from
                          (
                            SELECT
                              max(move.date) as date --FROM account_payment payment
                            FROM
                              account_move move --ON move.id = payment.move_id
                              JOIN account_move_line line ON line.move_id = move.id
                              JOIN account_partial_reconcile part ON part.debit_move_id = line.id
                              OR part.credit_move_id = line.id
                              JOIN account_move_line counterpart_line ON part.debit_move_id = counterpart_line.id
                              OR part.credit_move_id = counterpart_line.id
                              JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                              JOIN account_account account ON account.id = line.account_id
                            WHERE
                              account.account_type IN (
                                'asset_receivable', 'liability_payable'
                              ) --AND payment.id IN %(payment_ids)s
                              AND invoice.id in (paid_invoices.id)
                              AND line.id != counterpart_line.id
                              AND invoice.move_type in ('out_invoice')
                            GROUP BY
                              move.date
                          ) as dates
                      )
                    group by
                      paid_invoices.partner_id,
                      paid_invoices.company_id
                    UNION
                    select
                      vals.partner_id,
                      vals.company_id,
                      sum(vals.amount_total) as amount,
                      count(vals.id) as qty
                    From
                      (
                        select
                          ai.partner_id,
                          ai.company_id,
                          ai.id,
                          case when ai.currency_id = com.currency_id then ai.amount_untaxed else round(
                            (
                              ai.amount_untaxed / coalesce(
                                (
                                  select
                                    rate
                                  from
                                    get_nearest_currency_rate(
                                      ai.invoice_date :: date, ai.company_id
                                    )
                                  where
                                    currency_id = ai.currency_id
                                ),
                                1
                              )
                            ),
                            2
                          ) end as amount_total
                        from
                          account_move as ai
                          inner join res_company com on com.id = ai.company_id

                        where
                          ai.payment_state in ('paid', 'in_payment', 'reversed')
                          and ai.move_type = 'out_invoice'
                          and ai.invoice_date >= date_limit
                          and ai.partner_id = ANY(partner_ids)
                          and 1 = case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',com.id)),']') in ('[]') and
						 	ai.journal_id in (select id from account_journal where active = 't') then 1
						  else case when CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',com.id)),']') not in ('[]')
						  and ai.journal_id = any(
                                        string_to_array(
                                          replace(
                                            replace(
                                              replace(CONCAT('[',(select icp.value from ir_config_parameter icp where icp.key = CONCAT('setu_customer_rating.grace_days_journal_ids_',com.id)),']'), '[', ''),
                                              ']',
                                              ''
                                            ),
                                            ' ',
                                            ''
                                          ),
                                          ','
                                        ):: int[]
                                      ) then 1 else 0 end end
                          and (
                            select
                              invoice_date_due
                            from
                              account_move
                            where
                              id = ai.id
                          ):: date + grace_days_to_paid_invoice < --(select max(rel.date) as max_date from account_payment as ap
                          --    inner join account_move as rel on rel.payment_id = ap.id where rel.ref = ai.name)::date
                          (
                            SELECT
                              max(date)
                            from
                              (
                                SELECT
                                  max(move.date) as date --FROM account_payment payment
                                FROM
                                  account_move move --ON move.id = payment.move_id
                                  JOIN account_move_line line ON line.move_id = move.id
                                  JOIN account_partial_reconcile part ON part.debit_move_id = line.id
                                  OR part.credit_move_id = line.id
                                  JOIN account_move_line counterpart_line ON part.debit_move_id = counterpart_line.id
                                  OR part.credit_move_id = counterpart_line.id
                                  JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                                  JOIN account_account account ON account.id = line.account_id
                                WHERE
                                  account.account_type IN (
                                    'asset_receivable', 'liability_payable'
                                  ) --AND payment.id IN %(payment_ids)s
                                  AND invoice.id in (ai.id)
                                  AND line.id != counterpart_line.id
                                  AND invoice.move_type in ('out_invoice')
                                GROUP BY
                                  move.date
                              ) as dates
                          ) --group by ai.partner_id,ai.id
                          ) as vals
                    group by
                      vals.partner_id,
                      vals.company_id
                  ) as vals
                group by
                  vals.partner_id,
                  vals.company_id
              ) as
            values
            UNION
              --Another one
            select
              invoice_data.partner_id as partner_id,
              invoice_data.company_id as company_id,
              0 as avg_sales_score,
              0 as average_monthly_amount,
              0 as average_amount_sales_average,
              0 as average_amount_refund_average,
              0 as avg_refund_score,
             -- 0 as sales_average_for_refund_percentage,
              --0 as refund_average_for_refund_percentage,
              0 as due_date_score_amt,
			  0 as due_date_amount,
              0 as due_date_qty,
			  0 as due_qty,
              --(select pre_score from score_conf_line_price where score_conf_id = score_conf_amt_invoices_due_after_x_days_id and total_amount >= from_price and total_amount <= to_price) as due_after_60_amt,
              --(select pre_score from score_conf_line_qty where score_conf_id = score_conf_qty_invoice_paid_after_x_days_id and total_qty >= from_quantity and total_qty <= to_quantity) as due_after_60_qty,
              (
                select
                  pre_score
                from
                  score_conf_line_price lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'amt_invoice_due'
                  and sc.company_id = invoice_data.company_id
                  and total_amount >= lin.from_price
                  and total_amount <= lin.to_price
              ) as due_after_60_amt,
			  total_amount as due_after_60_amount,
              (
                select
                  pre_score
                from
                  score_conf_line_qty lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'qty_invoice_due'
                  and sc.company_id = invoice_data.company_id
                  and total_qty >= lin.from_quantity
                  and total_qty <= lin.to_quantity
              ) as due_after_60_qty,
			  total_qty as due_after_60_quantity,
              0 as pre_cancel_score,
              0 as avg_pay_score,
			  0 as avg_pay_days
            from
              (
                select
                  invs_data.partner_id,
                  invs_data.company_id,
                  max(invs_data.total_amount) as total_amount,
                  max(invs_data.total_qty) as total_qty
                from
                  (
                    select
                      ai.partner_id,
                      ai.company_id,
                      0 as total_amount,
                      0 as total_qty
                    from
                      (
                        select
                          partner_id,
                          company_id
                        from
                          account_move as ai
                        where
                          ai.payment_state in ('paid', 'in_payment', 'reversed')
                          and ai.invoice_date >= date_limit
                          and ai.move_type = 'out_invoice' and ai.l10n_mx_edi_cfdi_uuid is not null
                          and ai.partner_id = ANY(partner_ids)
                      ) as ai
                    group by
                      ai.partner_id,
                      ai.company_id
                    UNION
                    select
                      ai.partner_id,
                      ai.company_id,
                      sum(
                        case when ai.currency_id = com.currency_id then ai.amount_untaxed else round(
                          (
                            ai.amount_untaxed / coalesce(
                              (
                                select
                                  rate
                                from
                                  get_nearest_currency_rate(
                                    ai.invoice_date :: date, ai.company_id
                                  )
                                where
                                  currency_id = ai.currency_id
                              ),
                              1
                            )
                          ),
                          2
                        ) end
                      ) as total_amount,
                      count(ai.id) as total_qty
                    from
                      account_move as ai
                      inner join res_company com on com.id = ai.company_id
                    where
                      ai.payment_state in ('not_paid', 'partial')
                      and ai.invoice_date >= date_limit
                      and ai.state != 'cancel'
                      and ai.move_type = 'out_invoice'
                      and invoice_due_date_limit > invoice_date_due and ai.l10n_mx_edi_cfdi_uuid is not null
                      and ai.partner_id = ANY(partner_ids)
                    group by
                      ai.partner_id,
                      ai.company_id
                  ) as invs_data
                group by
                  invs_data.partner_id,
                  invs_data.company_id
              ) as invoice_data
            UNION
              --Another one
            select
              avg_pay_dates.partner_id as partner_id,
              avg_pay_dates.company_id as company_id,
              0 as avg_sales_score,
              0 as average_monthly_amount,
              0 as average_amount_sales_average,
              0 as average_amount_refund_average,
              0 as avg_refund_score,
             -- 0 as sales_average_for_refund_percentage,
             -- 0 as refund_average_for_refund_percentage,
              0 as due_date_score_amt,
			  0 as due_date_amount,
              0 as due_date_qty,
			  0 as due_qty,
              0 as due_after_60_amt,
			  0 as due_after_60_amount,
              0 as due_after_60_qty,
			  0 as due_after_60_quantity,
              0 as pre_cancel_score,
              case when avg_pay_dates.avg_days <= 0 then (
                select
                  max(pre_score)
                from
                  score_conf_line_qty lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'avg_payment_days'
                  and sc.company_id = avg_pay_dates.company_id
              ) else (
                select
                  pre_score
                from
                  score_conf_line_qty lin
                  inner join score_conf sc on sc.id = lin.score_conf_id
                where
                  sc.calculation_formula = 'avg_payment_days'
                  and sc.company_id = avg_pay_dates.company_id
                  and avg_days >= lin.from_quantity
                  and avg_days <= lin.to_quantity
              ) end avg_pay_score,
			  avg_days as avg_pay_days
            from
              (
                SELECT
                  invoice.partner_id,
                  invoice.company_id,
                  ceil(
                    AVG(
                      move.date - invoice.invoice_date_due
                    )
                  ) as avg_days --FROM account_payment payment
                From
                  account_move move --ON move.id = payment.move_id
                  JOIN account_move_line line ON line.move_id = move.id
                  JOIN account_partial_reconcile part ON part.debit_move_id = line.id
                  OR part.credit_move_id = line.id
                  JOIN account_move_line counterpart_line ON part.debit_move_id = counterpart_line.id
                  OR part.credit_move_id = counterpart_line.id
                  JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                  JOIN account_account account ON account.id = line.account_id
                WHERE
                  account.account_type IN (
                    'asset_receivable', 'liability_payable'
                  ) --AND payment.id IN %(payment_ids)s
                  --AND invoice.id in (ai.id)
                  AND line.id != counterpart_line.id
                  AND invoice.move_type in ('out_invoice')
                  AND invoice.payment_state in (
                    'paid', 'in_payment', 'reversed',
                    'partial'
                  )
                group by
                  invoice.partner_id,
                  invoice.company_id
              ) as avg_pay_dates
          ) as data
		 where data.partner_id = ANY (partner_ids)
        group by
          data.partner_id,
          data.company_id

      ) as main_data
    order by
      total_score desc
    )as cs2 where cs.partner_id = cs2.partner_id and cs.company_id = cs2.company_id
    and cs.partner_id = ANY (partner_ids);  --MOD;


END; $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
