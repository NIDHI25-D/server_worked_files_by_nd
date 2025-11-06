--create schema if not exists datastudio_reports AUTHORIZATION odoo14_datastudio;
--DROP view IF EXISTS datastudio_reports.view_of_prod_tmp_basic_info;
CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.materialized_view_of_prod_tmp_basic_info_view as
with selection_fields_value as (select imf.name, imfs.value,regexp_replace(to_json(imfs.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g') as field_value from public.ir_model im
        join public.ir_model_fields imf on imf.model_id = im.id
        join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
        where im.model = 'product.template' and imf.name in ('product_type_marvelsa','l10n_mx_edi_hazard_package_type')
    )
select
            pt.id as prod_temp_id,
            pt.is_published as "website_published",
            trim((select regexp_replace(to_json(pt.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as prod_name,
            pp.id as prod_variant_id,
            pb.id as prod_brand_id,
            pb.name as prod_brand_name,
            pt.sale_ok as can_be_sold,
            pt.purchase_ok as can_be_purchased,
            coalesce(pp.meli_pub,false) as is_published_in_ml,
            -- pt.meli_update_stock_blocked as prod_block_update_stock,
             pt.product_type_marvelsa as product_type_marvelsa_id,
            trim((select field_value from selection_fields_value where name='product_type_marvelsa' and value = pt.product_type_marvelsa)) as product_type_marvelsa,
            pt.can_be_used_for_advance_reordering as use_for_adv_reordering,
            pt.type as prod_type,
            pc.id as prod_categ_id,
            pc.complete_name as prod_categ_name,
            pp.default_code as prod_internal_ref,
            --mcr.dest_id as prod_competibles_id,
             STRING_AGG(distinct mc.name,',')
             as prod_competibles_name,
            pro_tempo.id as prod_tempo_id,
            pro_tempo.name as prod_tempo_name,
            pt.is_on_catalogue as prod_is_on_catelog,
            --mmr.marcadest_id as prod_marcas_id,
            STRING_AGG(distinct mm.name,',') as prod_marcas_name,
            --mrr.refaoriginaldest_id as prod_refaccion_original_id,
            STRING_AGG(distinct mr.name,',') as prod_refaccion_original_name,
            puc.id as UNSPSC_id,
            puc.code || ' ' || trim(regexp_replace(to_json(puc.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')) as UNSPSC_name,
            l10n_tarif_frac.id as tarrif_fraction_id,
            l10n_tarif_frac.name as tarrif_fraction_name,
            uu.id as UMT_aduana_id,
            trim(regexp_replace(to_json(uu.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
         as UMT_aduana_name,
            trim((select regexp_replace((select regexp_replace(to_json(pt.description->'en_US'::text)::varchar, '<[^>]*>', '', 'g'))::varchar,'[^%,/\.\w]+',' ','g'))) as prod_internal_notes,
            pt.list_price as prod_sales_price,
            pp.presale_price_incl_tax as pre_sale_price,
            --STRING_AGG(ptr.tax_id,',') as customer_taxes_id,
            STRING_AGG(distinct trim(regexp_replace(to_json(at.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')),',') as customer_taxes_name,
            -- prop.standard_price as prod_cost,
         (pp.standard_price ->> '1')::float as prod_cost, --changed
            uu2.id as unit_of_measure_id,
            trim((select regexp_replace(to_json(uu2.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as unit_of_measure_name,
            uu3.id as purchase_unit_measure_id,
            trim((select regexp_replace(to_json(uu3.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as purchase_unit_measure_name,
            pt.invoice_policy as prod_invoice_policy,
            pt.expense_policy as prod_re_invoice_expense,
            --por.dest_id as optional_products_id,
            STRING_AGG(distinct trim(regexp_replace(to_json(pt2.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')),',') as optional_products_name,
            trim(regexp_replace(to_json(pt.description_sale->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
             as prod_sales_description,
            pt.available_in_pos as avail_in_pos,
         STRING_AGG(DISTINCT trim(regexp_replace(to_json(pos_categ.name -> 'en_US')::varchar, '[^%,/\.\w]+', ' ', 'g')), ',') as pos_categories_name,
            pt.to_weight as prod_to_weight_with_scale,
            pt.purchase_method as prod_control_policy,
            trim(regexp_replace(to_json(pt.description_purchase->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
             as prod_purchase_description,
            pp.weight as prod_weight,
            pp.volume as prod_volume,
            pp.length as prod_length,
            pp.whidth as prod_width,
            pp.high as prod_high,
            pt.hs_code as prod_hs_code,
            -- pt.produce_delay as mnf_lead_time,
            pt.sale_delay as customer_lead_time,
            trim(regexp_replace(to_json(pt.description_pickingout->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
            as prod_delivery_order_desc,
            trim(regexp_replace(to_json(pt.description_pickingin ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
             as reciept_desc,
            trim(regexp_replace(to_json(pt.description_picking ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))
             as prod_interna_tranf_desc,
            ru.id as responsible_id,
            rp.name as responsible_name,
            sl_production.id as production_location_id,
            sl_production.name as production_location_name,
            sl_inventory.id as inventory_location_id,
            sl_inventory.name as inventory_location_name,
            aa.id as income_account_id,
            COALESCE((aa.code_store ->> '1')::text, '') ||' '|| trim(regexp_replace(to_json(aa.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')) as income_account_name,
            aa_expense.id as expense_account_id,

            COALESCE(aa_expense.code_store::json->>'1' , '')  ||' '|| trim(regexp_replace(to_json(aa_expense.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')) as expense_account_name,
            aa_price_diff.id as price_difference_account_id,
            COALESCE(aa_price_diff.code_store::json->>'1', '')  ||' '|| trim(regexp_replace(to_json(aa_price_diff.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')) as price_difference_account_name,
            pp.barcode as product_barcode,
            STRING_AGG(distinct trim(regexp_replace(to_json(ctag.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')),',') as tag_name,
            pt.discontinued as discontinued,
            partner.name as category_manager,
            origindb.origin as origin,
            pt.l10n_mx_edi_hazardous_material_code_id as hazardous_material_designation_code_mx,
            trim((select field_value from selection_fields_value where name = 'l10n_mx_edi_hazard_package_type' and value = pt.l10n_mx_edi_hazard_package_type)) as "hazardous_packaging_mx",
            ifl.name as import_factor_level,
            pt.competition_level_id as competition_level,
            STRING_AGG(distinct trim(regexp_replace(to_json(prot.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')),',') as industry,
            STRING_AGG(distinct trim((select regexp_replace(to_json(pt_name.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))),',') as additional_product_tag

          From public.product_product pp
                   join public.product_template pt on pt.id = pp.product_tmpl_id
            Left join public.product_category pc on pc.id = pt.categ_id
            Left join public.product_temporary pro_tempo on pro_tempo.id = pt.temporary_id
            Left join public.product_unspsc_code puc on puc.id = pt.unspsc_code_id
            Left join public.l10n_mx_edi_tariff_fraction l10n_tarif_frac on pt.l10n_mx_edi_tariff_fraction_id = l10n_tarif_frac.id
            Left join public.uom_uom uu on uu.id = pt.l10n_mx_edi_umt_aduana_id
            Left join public.uom_uom uu2 on uu2.id = pt.uom_id
            Left join public.uom_uom uu3 on uu3.id = pt.uom_po_id
            Left join public.product_optional_rel por on por.src_id = pt.id
            Left join public.product_template pt2 on pt2.id = por.dest_id
            -- Left join public.pos_category pos_cat on pos_cat.id = pt.pos_categ_id
         left join public.pos_category_product_template_rel pcptr on pcptr.product_template_id = pt.id
         left join public.pos_category pos_categ on pos_categ.id = pcptr.pos_category_id
            Left join public.product_brand pb on pb.id = pt.product_brand_id
            Left join public.marvelfields_compatible_rel mcr on mcr.src_id = pt.id
            Left join public.marvelfields_compatible mc on mc.id = mcr.dest_id
            Left join public.marvelmarcas_marca_rel mmr on mmr.marcasrc_id = pt.id
            Left join public.marvelmarcas_marca mm on mm.id = mmr.marcadest_id
            Left join public.marvelmarcas_refaoriginal_rel mrr on mrr.refaoriginalsrc_id = pt.id
            Left join public.marvelmarcas_refaoriginal mr on mr.id = mrr.refaoriginaldest_id
            Left join public.product_taxes_rel ptr on ptr.prod_id = pt.id
            Left join public.account_tax at on at.id = ptr.tax_id
            LEFT JOIN public.res_users ru on ru.id = (pt.responsible_id ->> '1')::integer
            Left JOIN public.res_partner rp on rp.id = ru.partner_id
            LEFT JOIN public.ir_model_fields imf on imf.name = 'property_stock_production' and imf.model ='product.template'
            LEFT JOIN public.stock_location sl_production on sl_production.id = (pt.property_stock_production ->> '1')::integer
            LEFT JOIN public.ir_model_fields imf2 on imf2.name = 'property_stock_inventory' and imf2.model ='product.template'
            LEFT JOIN public.stock_location sl_inventory on sl_inventory.id = (pt.property_stock_inventory ->> '1')::integer
         LEFT JOIN public.account_account aa on aa.id = (pt.property_account_income_id ->> '1')::integer
         LEFT JOIN public.account_account aa_expense  on aa_expense.id = (pt.property_account_expense_id ->> '1')::integer
         LEFT JOIN public.account_account aa_price_diff on aa_price_diff.id = (pt.property_account_creditor_price_difference ->> '1')::integer
            LEFT JOIN public.crm_id ct on pt.id = ct.tag_id
            LEFT JOIN public.crm_tag ctag on ctag.id = ct.crm_tag_id

            LEFT JOIN public.res_users ruser on ruser.id = pt.category_manager
            LEFT JOIN public.res_partner partner on partner.id = ruser.partner_id
            LEFT JOIN public.origin_database origindb on origindb.id = pt.origin_id
            LEFT JOIN public.import_factor_level ifl on ifl.id = pt.import_factor_level_id
            LEFT JOIN public.product_tag_product_template_rel ptptr on ptptr.product_template_id = pt.id
            LEFT JOIN public.product_tag prot on prot.id = ptptr.product_tag_id

            LEFT JOIN public.product_tag_product_product_rel ptpp on ptpp.product_product_id = pp.id
            LEFT JOIN public.product_tag pt_name on pt_name.id = ptpp.product_tag_id

            where pp.active = 't' --and pt.id = 80934
            group by
            pt.id ,
            pt.name,
            pp.id ,
            pb.id ,
            pb.name ,
            pt.sale_ok ,
            pt.purchase_ok ,
            pp.meli_pub,
            --pt.meli_update_stock_blocked as prod_block_update_stock,
             pt.product_type_marvelsa,
            pt.can_be_used_for_advance_reordering ,
            pt.type ,
            pc.id ,
            pc.complete_name ,
            pp.default_code ,
            --mcr.dest_id,
            --mc.name ,
            pro_tempo.id ,
            pro_tempo.name ,
            pt.is_on_catalogue ,
            --mmr.marcadest_id ,
            --mm.name ,
            --mrr.refaoriginaldest_id ,
            --mr.name ,
            puc.id ,
            puc.code , puc.name ,
            l10n_tarif_frac.id ,
            l10n_tarif_frac.name ,
            uu.id ,
            uu.name ,
            pt.description ,
            pt.list_price ,
            --ptr.tax_id ,
            --at.name ,
            pp.standard_price , -- prop.value_float ,
            uu2.id ,
            uu2.name ,
            uu3.id ,
            uu3.name ,
            pt.invoice_policy,
            pt.expense_policy,
           -- por.dest_id ,
            -- pt2.name ,
            pt.description_sale ,
            pt.available_in_pos ,
            pt.to_weight ,
            pt.purchase_method ,
            pt.description_purchase ,
            pp.weight ,
            pp.volume ,
            pp.length ,
            pp.whidth ,
            pp.high,
            pt.hs_code ,
            -- pt.produce_delay ,
            pt.sale_delay ,
            pt.description_pickingout ,
            pt.description_pickingin ,
            pt.description_picking ,
            ru.id ,
            rp.name,
            sl_production.id ,
            sl_production.name ,
            sl_inventory.id,
            sl_inventory.name ,
            aa.id ,
            aa.code_store , aa.name ,
            aa_expense.id,
            aa_expense.code_store ,aa_expense.name ,
            aa_price_diff.id,
            aa_price_diff.code_store , aa_price_diff.name,
            pp.barcode,
            partner.name,
            origindb.origin,
            ifl.name,
             pp.presale_price_incl_tax;


ALTER TABLE datastudio_reports.materialized_view_of_prod_tmp_basic_info_view
  OWNER TO odoo14_datastudio;