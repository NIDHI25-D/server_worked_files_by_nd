DROP FUNCTION IF EXISTS public.get_employee_attendance_data(integer[], integer[], date, date, numeric, text);
CREATE OR REPLACE FUNCTION public.get_employee_attendance_data(
    IN department_ids integer[],
    IN employee_ids integer[],
    IN start_date date,
    IN end_date date,
    IN worked_hours numeric,
    IN worked_hours_operator text)
  RETURNS TABLE(employee_id integer, department_id integer, expected_working_hours double precision, holiday_hours double precision, absence_hours double precision, real_worked_hours double precision, total_hours double precision, difference double precision) AS
$BODY$
    DECLARE
        tr_start_date timestamp without time zone := (start_date || ' 00:00:01')::timestamp without time zone;
        tr_end_date timestamp without time zone:= (end_date || ' 23:59:59')::timestamp without time zone;

BEGIN
    Return Query

    with rc_holidays as (
        Select * from (
            Select
                shift.id as shift_id,
                generate_series(g_leaves.date_from, g_leaves.date_to, '1 day'::interval)::date as leave_date,
                shift.hours_per_day
            from resource_calendar shift
            Left Join resource_calendar_leaves g_leaves on g_leaves.calendar_id = shift.id
            where g_leaves.date_from::date >= start_date --and g_leaves.date_from::date <= end_date and g_leaves.date_to::date >= start_date
            --and g_leaves.date_to::date <= end_date
            and g_leaves.resource_id is null
            )gl
        where gl.leave_date>=start_date and gl.leave_date<=end_date
        ),
    rc_workhours as (
        Select
            shift.id as shift_id,
            generate_series(start_date, end_date, '1 day'::interval)::date as work_date,
            shift.hours_per_day
        from resource_calendar shift
        )

    Select data.* From
    (
    Select
        attendance.employee_id, attendance.department_id,
        workdays.work_hours as expected_worked_hours,
        0::double precision as holiday_hours,
        0::double precision as absence_hours,
        0::double precision as real_worked_hours,
        0::double precision as total,
        0::double precision as difference
    From
    (
        Select
            D.employee_id,
            D.department_id,
            D.shift_id,
            sum(D.real_worked_hours) as real_worked_hours,
            max(D.hours_per_day) as hours_per_day
        From
        (
            Select
                att.employee_id,
                emp.department_id,
                sum(att.worked_hours) as real_worked_hours,
                shift.hours_per_day,
                shift.id as shift_id
            From
                hr_attendance att
            Inner Join hr_employee emp on emp.id = att.employee_id
            Left Join hr_department dept on dept.id = emp.department_id
            Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
            where emp.active=True and emp.employee_attendance_report_working_hour_id is not null and
            att.check_in >= tr_start_date and att.check_in <= tr_end_date and att.check_out >= tr_start_date and att.check_out <= tr_end_date
                and 1 = case when array_length(department_ids,1) >= 1 then
                case when emp.department_id = ANY(department_ids) then 1 else 0 end
                else 1 end
                and 1 = case when array_length(employee_ids,1) >= 1 then
                case when att.employee_id = ANY(employee_ids) then 1 else 0 end
                else 1 end
                Group by att.employee_id, emp.department_id, shift.hours_per_day, shift.id

            Union All

            Select
                emp.id,
                emp.department_id,
                0 as real_worked_hours,
                shift.hours_per_day,
                shift.id
            From hr_employee emp
            Left Join hr_department dept on dept.id = emp.department_id
            Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
            where emp.active=True and emp.employee_attendance_report_working_hour_id is not null and
	    1 = case when array_length(department_ids,1) >= 1 then
                case when emp.department_id = ANY(department_ids) then 1 else 0 end
                else 1 end
                and 1 = case when array_length(employee_ids,1) >= 1 then
                case when emp.id = ANY(employee_ids) then 1 else 0 end
                else 1 end
                --Group by emp.id, emp.department_id, shift.hours_per_day, shift.id
        )D
        group by D.employee_id, D.department_id, D.shift_id
    )attendance

    Left Join
    (
        Select leave_data.employee_id,
            leave_data.hours_per_day,
            sum(leave_data.absence_hours) as absence_hours,
            sum(leave_data.holiday_type_hours) as holiday_type_hours
        From
        (
		Select LD.employee_id,
			LD.leave_date,
			--max(LD.leave_hours) as leave_hours,
			case when not LD.is_holiday_type then max(LD.leave_hours) else 0 end as absence_hours,
            case when LD.is_holiday_type then max(LD.leave_hours) else 0 end as holiday_type_hours,
			LD.hours_per_day,
			LD.shift_id
		     From
		(
		    select
		        nld.employee_id,
		        nld.leave_date,
			    max(nld.leave_hours) as leave_hours,
			    nld.hours_per_day,
			    nld.shift_id,
			    coalesce(nld.is_holiday_type,false) as is_holiday_type
		     from (
		    SELECT
			leave.employee_id,
			generate_series(date_from, date_to, '1 day'::interval)::date as leave_date,
			case when leave.request_unit_hours then EXTRACT(EPOCH FROM (leave.date_to - leave.date_from))/3600 else
			case when number_of_days > 1 then 1 else number_of_days end * shift.hours_per_day
			end as leave_hours,
			shift.hours_per_day,
			shift.id as shift_id,
            leave_type.is_holiday_type as is_holiday_type
		    from
			hr_leave leave
		    Inner Join hr_employee emp on emp.id = leave.employee_id
		    Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
		    Left Join hr_leave_type leave_type on leave_type.id = leave.holiday_status_id
		    where leave.state = 'validate' and date_from >= start_date and emp.employee_attendance_report_working_hour_id is not null
			and 1 = case when array_length(department_ids,1) >= 1 then
			case when emp.department_id = ANY(department_ids) then 1 else 0 end
			else 1 end
			and 1 = case when array_length(employee_ids,1) >= 1 then
			case when leave.employee_id = ANY(employee_ids) then 1 else 0 end
			else 1 end)nld
			group by nld.employee_id, nld.leave_date, nld.hours_per_day, nld.shift_id, nld.is_holiday_type
		)LD
		Inner Join resource_calendar_attendance cal_att on cal_att.calendar_id = LD.shift_id and (extract(isodow from leave_date) - 1)::character varying = cal_att.dayofweek
		group by LD.employee_id, LD.leave_date, LD.hours_per_day, LD.shift_id, LD.is_holiday_type
        )leave_data
        where leave_date >= start_date and leave_date <= end_date
        Group by leave_data.employee_id, hours_per_day
    )leave
    on leave.employee_id = attendance.employee_id
    -- Left Join holidays h on h.employee_id = attendance.employee_id
    Left Join
    (
        Select
            rc.shift_id,
            sum(rca.hour_to - rca.hour_from) as holiday_hours
        from rc_holidays rc
        Inner Join resource_calendar_attendance rca on rca.calendar_id = rc.shift_id and (extract(isodow from leave_date) - 1)::character varying = rca.dayofweek
        group by rc.shift_id
    ) holidays on holidays.shift_id = attendance.shift_id
    Left Join
    (
        Select
            rc.shift_id,
            sum(rca.hour_to - rca.hour_from) as work_hours
        from rc_workhours rc
        Inner Join resource_calendar_attendance rca on rca.calendar_id = rc.shift_id and (extract(isodow from work_date) - 1)::character varying = rca.dayofweek
        group by rc.shift_id
    ) workdays on workdays.shift_id = attendance.shift_id
    )data
    where 1 = case when coalesce(worked_hours, 0) <= 0 then 1 else
    case
    when worked_hours_operator = 'more' and data.total > worked_hours then 1
    when worked_hours_operator = 'less' and data.total < worked_hours then 1
    when worked_hours_operator = 'more_or_equal' and data.total >= worked_hours then 1
    when worked_hours_operator = 'less_or_equal' and data.total <= worked_hours then 1
    else 0 end
    end;


    END; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
