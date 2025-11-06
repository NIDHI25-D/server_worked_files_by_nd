CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.get_journal_items_view as
with analytic_account as (
	select id as move_line_id,
		   array_to_string(array_agg(x.cola), ',') as analytic_distribution_id,
 		   array_to_string(array_agg(x.colb), ',') as analytic_distribution
	from public.account_move_line aml
	cross join lateral json_each(aml.analytic_distribution::json) as x(cola, colb) where aml.analytic_distribution is not null
	group by id
)
select
        aml.id as move_line_id,
        aml.name as move_line_name,
        aml.partner_id as partner_id,
        rp.name as partner_name,
        aml.account_id as account_id,
		trim((select regexp_replace(to_json(aa.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as account_name,
        -- aa.code || ''|| aa.name as account_name,
        aml.debit as debit,
        aml.credit as credit,
        aml.quantity as quantity,
        aml.move_id as move_id,
        am.name  as move_name,--|| ' (' || aml.ref || ')' as move_name,
        aml.date as date,
        aml.followup_line_id as followup_level_id,
                trim((select regexp_replace(to_json(affl.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as followup_level_name,
        -- aml.last_followup_date as followup_date, remove field last_followup_date
        aml.date_maturity as due_date,
        rc.symbol || ' '|| aml.amount_currency as amount_in_currency,
        aml.blocked as no_followup,
		account.analytic_distribution_id as analytic_distribution_id,
		account.analytic_distribution as analytic_distribution_percentage,
		aml.analytic_distribution as analytic_distribution,
        -- aml.tax_audit as tax_audits_string, remove field tax_audit
        aml.product_id as product_id,
        pp.default_code as prod_internal_ref,
        trim((select regexp_replace(to_json(pt.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as prod_name

from public.account_move_line aml
        left join public.res_partner rp on rp.id = aml.partner_id
        left join public.account_account aa on aa.id = aml.account_id
        left join public.account_move am on am.id = aml.move_id
        left join public.account_followup_followup_line affl on affl.id = aml.followup_line_id
        left join public.res_currency rc on rc.id=aml.currency_id

        LEFT JOIN analytic_account account ON account.move_line_id=aml.id

        left join public.product_product pp on pp.id = aml.product_id
        left join public.product_template pt on pt.id = pp.product_tmpl_id
 where  aml.display_type not in ('line_section', 'line_note') and am.state != 'cancel' and aml.parent_state = 'posted' and aml.date >= '2022-01-01';

 ALTER TABLE datastudio_reports.get_journal_items_view
  OWNER TO odoo14_datastudio;
