CREATE MATERIALIZED view IF NOT EXISTS datastudio_reports.materialized_view_of_fleet_service as
with field_value as (select imf.name,imfs.value,regexp_replace(to_json(imfs.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')  as field_value from public.ir_model im
		join public.ir_model_fields imf on imf.model_id = im.id
		join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
		where im.model = 'fleet.vehicle.log.services' and imf.name in ('state')),
field_values as (select imf.name,imfs.value,regexp_replace(to_json(imfs.name->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g')  as field_values from public.ir_model im
		join public.ir_model_fields imf on imf.model_id = im.id
		join public.ir_model_fields_selection imfs on imfs.field_id = imf.id
		where im.model = 'fleet.vehicle' and imf.name in ('odometer_unit'))
select
	flt.id as id,
	flt_vehicle.license_plate as license_plate,
	trim((select field_value from field_value where name = 'state' and value = flt.state)) as status,
	flt.description as description,
	trim((select regexp_replace(to_json(flt_type.name ->'en_US'::text)::varchar,'[^%,/\.\w]+',' ','g'))) as service_type,
	flt.date as date,
	flt.amount as amount,
	rp.name as vendor,
	flt_vehicle.name as vehicle,
	rp_d.name as driver,
	COALESCE(flt_meter.value, 0) as odometer,
	trim((select field_values from field_values where name = 'odometer_unit' and value = flt_vehicle.odometer_unit)) as odometer_unit,
	flt.notes as notes
from public.fleet_vehicle_log_services flt
left join public.fleet_service_type flt_type on flt_type.id = flt.service_type_id
left join public.res_partner rp on rp.id = flt.vendor_id
left join public.fleet_vehicle flt_vehicle on flt_vehicle.id = flt.vehicle_id
left join public.res_partner rp_d on rp_d.id = flt.purchaser_id
left join public.fleet_vehicle_odometer flt_meter on flt_meter.id = flt.odometer_id

where flt.active='t';

ALTER TABLE datastudio_reports.materialized_view_of_fleet_service
  OWNER TO odoo14_datastudio;