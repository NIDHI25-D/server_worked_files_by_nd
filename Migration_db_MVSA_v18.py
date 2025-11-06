DOC : https://www.odoo.com/documentation/18.0/administration/upgrade.html

gcloud compute ssh --zone "us-central1-a" "us1alx002" --project "marvelsa-odoo"

-----------------
Process in cloud |
-----------------
login with user : us1alx002 --> cloud ssh
nidhi@us1alx002:~$ sudo su root
				   cd
root@us1alx002:  sudo su odoo18
2025-05-22 11:28:04 INFO: The secret token is 'HA428brG51h-_C5FIAsIGe8M0SCc03eMv6sXZgclc5oQYkkZkfrtL1-oIQ' 
root@us1alx002:~ pg_dump -h 10.54.160.60 --verbose --exclude-schema=datastudio_reports -U odoo16 -F c -f /bck/mvsa_staging.dump mvsa_production -W
odoo18@us1alx002:
					pg_dump -h 10.54.160.60 --verbose --exclude-schema=datastudio_reports -U odoo16 -F c -f /tmp/mvsa_staging.dump mvsa_production -W
					
					password : /*+-1!2@3#4$5%6^7&8*9(10)MVsarj (odoo16 conf)


					{here -c is enterprise code of last version 
						  -t is the target versiom i.e. new versiom
						  -x is experimental experience
					}
					python3 <(curl -s https://upgrade.odoo.com/upgrade) test -i /bck/mvsa_staging.dump -c M19061711465334 -t 18.0 -x

					OR 

					python <(curl -s https://upgrade.odoo.com/upgrade) test -d <your db name> -t <target version> (in doc)






		view_server_action_form
		password_security = res_config_settings_view_form					

Error : <xpath expr="//div[hasclass('oe_kanban_details')]/strong[1]" 
		view_product_variant_kanban_brand

Error : <xpath expr="//field[@name='show_operations']]"
		add_field_is_enable_create_picking

Error : <xpath expr="//button[@name='action_toggle_is_locked'][1]"
		view_picking_form_inherited

Error : <xpath expr="//form/group[2]/group[2]/field[@name='journal_id']"
		add_field_in_credit_note_wizard

Error : <xpath expr="//notebook/page[@name='other_information']/group[2]/group[@name='sale_reporting']//field[@name='opportunity_id']" position="attributes">
		sale_order_form_view_for_crm

Error : <xpath expr="//field[@name='pricelist_id']" position="replace">
		view_button_in_pricelist_repair_order

Error : <xpath expr="//header/button[@name='action_set_lost']"
		view_crm_lead_extend								

Error : <xpath expr="//field[@name='reserved_uom_qty']"
		add_field_reserve_used_qty_stock_picking		

raise ValidationError(_("The default pricelist must be included in the available pricelists."))
odoo.exceptions.ValidationError: The default pricelist must be included in the available pricelists.		

new_for_v18_may_26_2025_mvsa_production=# update pos_config set use_pricelist = 'f' where id in (6,7);


price_list : 
----------
config_ids = self.env['pos.config'].browse([1,6,7])
list_with_pricelist_ids = []
for i in config_ids:
    list_with_pricelist_ids.append([i,i.pricelist_id,i.available_pricelist_ids])
result = list_with_pricelist_ids

===========================================================================================
 pg_dump -h 127.0.0.1 --verbose --exclude-schema=datastudio_reports -U odoo16 -F c -f /tmp/mvsa_prod_v18.dump new_for_v18_may_26_2025_mvsa_production -W


gcloud compute scp --zone "us-central1-a" us1alx002:/bck/mvsa_staging.dump /home/setu20/workspace/odoo16/_dump/ --project "marvelsa-odoo"

update ir_ui_view set active='f' where arch_db::jsonb::text ilike '%view_server_action_form%';
and model='password.security';

/tmp/mvsa_prod_v18.dump


UPDATE ir_ui_view
SET active = FALSE
WHERE key IN (
    'view_product_variant_kanban_brand',
    'add_field_is_enable_create_picking',
    'view_picking_form_inherited',
    'add_field_in_credit_note_wizard',
    'sale_order_form_view_for_crm',
    'view_button_in_pricelist_repair_order',
    'view_crm_lead_extend',
    'add_field_reserve_used_qty_stock_picking'
);

-----------------------------------------------------------------------------------------------------------------------


Production server : pg_dump -h 10.77.160.199 -U odoo16 mdh_prod_06_feb --exclude-schema=datastudio_reports --verbose | gzip -9 > may_26_2025_mvsa_production.sql.gz

In local : 
--------
Started the db, applied the query
Uninstall : Budget forcasting, Cash forcasting
Removed groups from Docs of approval and ex

When in staging server apply host : 10.54.160.60 of V17 and instead of tmp use /bck/

setu20@setu20:~$ sudo su postgres
				 cd
				 pg_dump -h 127.0.0.1 --verbose --exclude-schema=datastudio_reports -U odoo16 -F c -f /tmp/mvsa_prod_v18.dump new_for_v18_may_26_2025_mvsa_production -W
setu20@setu20:~$ python3 <(curl -s https://upgrade.odoo.com/upgrade) test -i /tmp/mvsa_prod_v18.dump -c M19061711465334 -t 18.0 -x
				
				 sync the migrated filestore and original filestore
				------------------------------------------------------------------------
				 rsync -a  filestore mvsa_production  

				 Create db
setu20@setu20:~/workspace/odoo16/_dump/upgraded$ sudo su postgres
postgres@setu20:/home/setu20/workspace/odoo16/_dump/upgraded$  createdb odoo18_mvsa_staging_31st_may -O odoo18;
															   psql
postgres@setu20:/home/setu20/workspace/odoo16/_dump/upgraded$ sudo chmod 755 dump.sql
															   odoo18_mvsa_staging_31st_may=# \i dump.sql (this method is used to follow the process of gunzip)												




-----------------------------------------------------------------------------------------------------------------------

get_journal_items_view - [ Done by siddharth ]
get_product_template_stock_info_materialized_view [ Done by siddharth]
materialized_contact_view
materialized_view_of_fleet_service
materialized_view_of_prod_tmp_basic_info_view
materialized_view_of_product_by_vendor [ Done by siddharth ]
materialized_view_of_sale_order [ Done by siddharth ]
materialized_view_of_sale_order_line [ Done by siddharth ]
materialized_view_of_sale_order_line_invoice_rel [ Done by siddharth ]
