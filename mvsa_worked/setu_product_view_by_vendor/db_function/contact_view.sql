CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.materialized_contact_view as

with selection_fields_value as (select imf.name, imfs.value,regexp_replace(to_json(imfs.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g') as field_value from public.ir_model im
        join public.ir_model_fields imf on imf.model_id = im.id
        join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
        where im.model = 'res.partner' and imf.name in ('type','lang','l10n_mx_edi_usage','vendor_rule','l10n_mx_type_of_operation','l10n_mx_edi_fiscal_regime','l10n_mx_edi_external_trade_type')
    )
select  rs.id,
        rs.create_date as created_on,
         rs.contact_view_opportunity_count as opportunities_quantities,
         rs.contact_view_purchase_count as purchases_quantities,
        rs.contact_view_sale_count as sales_quantities,
         rs.contact_view_total_invoice as invoiced_amount,
         rs.contact_view_supplier_invoice_count as invoiced_vendor_quantities,
        count(distinct cc.id) as  claim_quantities,
        case when rs.is_company then 'Company' else 'Individual' end as company_type,
        rs.name as name,
        rel_part.name  as related_company,
        case when rs.parent_id is not null then rs_parent.hcategory_id else rs.hcategory_id end as category_id,
        case when rs.parent_id is not null then rph_parent.name else rph.name end as category,
        (select field_value from selection_fields_value where name='type' and value= rs.type) as address_type,
        rs.postal_code_id as postal_code_id,
         rs.zip || ',' || src.name || ',' || (select regexp_replace(to_json(rc.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')) || ',' || rcs.name as postal_code ,
        rs.street_name as address,
        rs.street_number as house,
        rs.street_number2 as door,
        rs.l10n_mx_edi_colony as colony,
                trim((select regexp_replace(to_json(locality.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as locality,
        trim((select regexp_replace(to_json(rc.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as city,
        rcs.name as state,
        rs.zip as zip_code,
        trim((select regexp_replace(to_json(rcu.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as country,
        rs.vat as rfc,
        rs.l10n_mx_edi_curp as curp,
        -- trim((select regexp_replace(to_json(ct.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as sale_team,
         rs.x_studio_fecha_de_alta as fetcha_de_alta,
        rs.l10n_mx_edi_operator_licence as operator_licence,
        rs.ncliente as numero_de_cliente,
         rs.x_studio_no_suplemento as no_suplemento,
                -- case when rs.loyalty_points is null then 0 else rs.loyalty_points end as loyalty_points,
        rs.function as job_position,
        rs.phone as phone,
        rs.mobile as mobile,
        rs.email as email,
        rs.website as website_link,
        trim((select regexp_replace(to_json(rpt.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as title,
        rl.name as language,

        string_agg(distinct trim(regexp_replace(to_json(rpc.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')),',') as tags,
--         string_agg(distinct classi_name.name,',') as clasificaciones,
--         string_agg(distinct sub_class_name.name,',') as subclases,
        sug.name as surtido_sugerido,
        rs.rutav as ruta,
         rs.x_studio_elite as elite,
        rpz.name as zone,
        sales.name as salesperson,
        trim((select regexp_replace(to_json(dc.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as delivery_method,
        trim((select regexp_replace(to_json(apt.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as sale_payment_term,
        trim((select regexp_replace(to_json(product_pri.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as  price_list,
        string_agg(distinct trim((select regexp_replace((select regexp_replace(to_json(del.name->'en_US'::text)::varchar, '<[^>]*>', '', 'g'))::varchar,'[^%,/\.\w]+',' ','g'))),',')
                 as prefered_delivery_method,
        rs.l10n_mx_edi_external_trade as need_external_trade,
        trim((select regexp_replace(to_json(apt_purchase.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as purchase_payment_term,
        res_cus.name as supplier_currency,
        (rs.barcode->>'1')::text as barcode,
                trim((select regexp_replace(to_json(acc_fiscal_pos.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as fiscal_position,
        payment_way_tab.name as payment_way,
        trim((select field_value from selection_fields_value where name='l10n_mx_edi_usage' and value= rs.l10n_mx_edi_usage)) as usage,
        rs.disable_inv_automatic_sign as disable_invoice_automatically_signed,
        case when rs.credit_limit is null then 0 else (rs.credit_limit->>'1')::float end as credit_limit, -- same as upper line
        rs.over_credit as allow_over_credit,
        rs.ref as reference,
        website.name as website,
                case when rs.property_stock_customer is null  then (select scl.complete_name from public.stock_location scl where scl.id = 9)
        else sl_cus.complete_name end as customer_location,
        case when rs.property_stock_supplier is null  then (select scl.complete_name from public.stock_location scl where scl.id = 8)
        else sl_sup.complete_name end as vendor_location,
        rs.minimum_reorder_amount as minimum_reorder_amount,
        trim((select field_value from selection_fields_value where name='vendor_rule' and value= rs.vendor_rule)) as vendor_rule,
        trim((select regexp_replace(to_json(rcu.demonym ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as l10n_mx_nationality,
        case when rs.parent_id is not null then (select field_value from selection_fields_value where name='l10n_mx_type_of_operation' and value= rs_parent.l10n_mx_type_of_operation)
        else trim((select field_value from selection_fields_value where name='l10n_mx_type_of_operation' and value= rs.l10n_mx_type_of_operation)) end as l10n_mx_type_of_operation,
                case when rs.property_account_receivable_id is null then (select (aa.code_store->>'1')::text || ',' || aa.name from public.account_account aa where aa.id = 444) else (acc_rec.code_store->>'1')::text || ',' || acc_rec.name  end as account_receivable,
                case when rs.property_account_payable_id is null then (select (aa.code_store->>'1')::text || ',' || aa.name from public.account_account aa where aa.id = 516) else (acc_pay.code_store->>'1')::text || ' ' || acc_pay.name end as account_payable,
        string_agg(distinct pd.name,',') as payment_days,
        case when rs.parent_id is not null then rs_col_par.name else rs_col.name end as collection_executive,
        trim((select regexp_replace(rs.comment, '<[^>]*>', '', 'g'))) as internal_notes,
        srs.name as rfm_segment,
        srscore.name as rfm_score,
        (rs.total_score->>'1')::integer as score, -- prop_total_score.value_integer as score,
        cus_rating.rating as rating,
        case when rs.parent_id is not null then rs_parent.name || ',' || rs.name else rs.name end as customer_score,
                rs_legal.name as legal_person,
                create_uid.name as created_by,
                trim((select regexp_replace(to_json(ppl.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')))
                 as monthly_proposal_pricelist,
                addenda.name as addenda,
                trim((select field_value from selection_fields_value where name='l10n_mx_edi_fiscal_regime' and value= rs.l10n_mx_edi_fiscal_regime)) as fiscal_regime,
                rs.l10n_mx_edi_no_tax_breakdown as no_tax_breakdown,
                trim((select field_value from selection_fields_value where name='l10n_mx_edi_external_trade_type' and value= rs.l10n_mx_edi_external_trade_type)) as external_trade

from        public.res_partner rs
--left join   public.res_users ru_credit on ru_credit.partner_id = rs.id
--left join   public.crm_lead cl on cl.partner_id = rs.id and cl.active='t'
left join   public.crm_claim cc on rs.id = cc.partner_id
left join   public.res_partner rel_part on rel_part.id = rs.parent_id
left join   public.res_partner_hcategory rph on rph.id = rs.hcategory_id
left join   public.sepomex_res_colony src on src.id = rs.postal_code_id
left join   public.res_city rc on rc.id = rs.city_id
left join   public.res_country_state rcs on rcs.id = rs.state_id
left join   public.l10n_mx_edi_res_locality locality on locality.id = rs.l10n_mx_edi_locality_id
left join   public.res_country rcu on rcu.id = rs.country_id
-- left join   public.crm_team ct on ct.id = rs.team_id
left join   public.res_partner_res_partner_category_rel tag on tag.partner_id = rs.id
left join   public.res_partner_category rpc on rpc.id = tag.category_id
-- left join   public.marvelfields_clasificaciones_rel classi on classi.src_id = rs.id
-- left join   public.marvelfields_clasificaciones classi_name on classi_name.id = classi.dest_id
-- left join   public.marvelfields_subclases_rel sub_class on sub_class.src_id = rs.id
-- left join   public.marvelfields_subclases sub_class_name on sub_class_name.id = sub_class.dest_id
left join   public.stock_warehouse sug on sug.id = rs.warehouse_sugerido_id
left join   public.res_partner_zone rpz on rpz.id = rs.zone_id
left join   public.res_users ru on ru.id = rs.user_id
left join   public.res_partner sales on sales.id = ru.partner_id
left join   public.delivery_carrier dc on (rs.property_delivery_carrier_id ->> '1')::integer = dc.id
left join   public.account_payment_term apt on (rs.property_payment_term_id ->> '1')::integer = apt.id
left join   public.delivery_carrier_res_partner_rel del_car_many on del_car_many.res_partner_id = rs.id
left join   public.delivery_carrier del on del.id = del_car_many.delivery_carrier_id
left join   public.account_payment_term apt_purchase on (rs.property_supplier_payment_term_id ->> '1')::integer = apt_purchase.id
left join   public.res_currency res_cus  on (rs.property_purchase_currency_id ->> '1')::integer = res_cus.id
left join   public.account_fiscal_position acc_fiscal_pos on (rs.property_account_position_id ->> '1')::integer = acc_fiscal_pos.id
left join   public.l10n_mx_edi_payment_method payment_way_tab on payment_way_tab.id = rs.l10n_mx_edi_payment_method_id
left join   public.website on website.id = rs.website_id
left join   public.stock_location sl_cus on (rs.property_stock_customer->>'1')::integer = sl_cus.id
left join   public.stock_location sl_sup on (rs.property_stock_supplier->>'1')::integer = sl_sup.id
left join   public.account_account acc_rec on (rs.property_account_receivable_id->>'1')::integer = acc_rec.id
left join   public.account_account acc_pay on (rs.property_account_payable_id->>'1')::integer = acc_pay.id
left join   public.res_partner rs_parent on rs.parent_id = rs_parent.id
-- left join   public.ir_property prop_loyalty_points on prop_loyalty_points.res_id = 'res.partner,' || rs.id and prop_loyalty_points.name = 'loyalty_points'
left join   public.res_partner_hcategory rph_parent on rph_parent.id = rs_parent.hcategory_id
left join   public.res_partner_paymnet_days_rel paymet_days_tab on paymet_days_tab.res_partner_id = (case when rs.parent_id is not null then rs_parent.id else rs.id end)
left join   public.payment_days pd on pd.id = paymet_days_tab.payment_days_id
left join   public.res_users ru_col on ru_col.id = rs.collection_executive_id
left join   public.res_partner rs_col on rs_col.id = ru_col.partner_id
left join   public.res_users ru_col_par on ru_col_par.id = rs_parent.collection_executive_id
left join   public.res_partner rs_col_par on rs_col_par.id = ru_col_par.partner_id

left join   public.setu_rfm_segment srs on srs.id = (rs.rfm_segment_id->>'1')::integer
left join   public.setu_rfm_score srscore on srscore.id = (rs.rfm_score_id->>'1')::integer
left join   public.res_partner_title rpt on rpt.id = rs.title
left join   public.customer_rating cus_rating on (rs.rating->>'1')::integer = cus_rating.id
left join    public.product_pricelist product_pri on product_pri.id = rs.contact_view_property_product_pricelist
-- left join   public.ir_property prop_credit_limit on prop_credit_limit.res_id = 'res.partner,' || rs.id and prop_credit_limit.name = 'credit_limit'

left join   public.res_lang rl on rs.lang = rl.code
left join   public.legal_person rs_legal on rs_legal.id = rs.legal_person_id
left join   public.product_pricelist ppl on ppl.id = rs.monthly_proposal_pricelist_id
left join   public.res_users rs_create on rs_create.id = rs.create_uid
left join   public.res_partner create_uid on create_uid.id = rs_create.partner_id
-- left join    public.ir_ui_view ui_view on ui_view.id = rs.l10n_mx_edi_addenda
left join    public.l10n_mx_edi_addenda addenda on addenda.id = rs.l10n_mx_edi_addenda_id
left join public.account_move am on am.partner_id = rs.id


where   rs.active = 't'
--and rs.contact_view_sale_count > 0
--and rs.id in (3798)


group by
                rs.id,rs.parent_id,rs_parent.l10n_mx_type_of_operation,rs_col_par.name,rs_parent.hcategory_id,rph_parent.name,
                -- rs.loyalty_points,
                rel_part.id,
                rs.is_company,rs.name,rel_part.name,rs.hcategory_id,rph.name,rs.type,rs.postal_code_id,src.name,rs.zip,rc.name,rcs.name,
                rs.function,rs.phone,rs.mobile,rs.email,rs.website,sug.name,rs.rutav,
                 rs.x_studio_elite ,
                rpz.name,
                rs.street_number,rs.street_number2,rs.l10n_mx_edi_colony,locality.name,rc.name,rcs.name,rs.zip,rcu.name,rs.vat,rs.ncliente,
                rs.street_name,rs.l10n_mx_edi_curp,
                -- ct.name,
                rs.x_studio_fecha_de_alta,rs.l10n_mx_edi_operator_licence,rs.ncliente,
                 rs.x_studio_no_suplemento,
                sales.name,dc.name,apt.name,product_pri.name,
                rs.l10n_mx_edi_external_trade,apt_purchase.name,
                acc_fiscal_pos.name,
                payment_way_tab.name,rs.l10n_mx_edi_usage,rs.disable_inv_automatic_sign,rs.over_credit,
                rs.ref,website.name,
                sl_cus.id,
                rs.property_stock_customer,
                rs.property_stock_supplier,
                sl_sup.id,rs.minimum_reorder_amount,rs.vendor_rule,res_cus.name,
                rcu.demonym,
                rs.l10n_mx_type_of_operation,
                acc_rec.name,
                acc_rec.code_store,
                acc_pay.code_store ,
                acc_pay.name,
                rs.property_account_receivable_id,
                rs.property_account_payable_id,
                rs_col.name,
                rl.name,
                          --res_con_pri_gro.pricelist_id,
                rs.comment,
                srs.name,srscore.name,
                rpt.name,
                rs.barcode ,
                rs.total_score,
                cus_rating.rating,rs.name,rs_parent.name,-- product_pri.name,
                rs_legal.name,ppl.name,
                create_uid.name,
                addenda.name,
                rs.credit_limit;

ALTER TABLE datastudio_reports.materialized_contact_view
  OWNER TO odoo14_datastudio;