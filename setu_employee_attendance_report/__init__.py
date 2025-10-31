from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def pre_init(cr):
    create_sp(cr)


def create_sp(cr):
    # Currently not used while install the module. Remove from the manifest.
    qry = """
        DROP FUNCTION IF EXISTS get_employee_attendance_data(integer[],integer[],date,date,numeric,text);

        CREATE OR REPLACE FUNCTION public.get_employee_attendance_data(
            IN department_ids integer[],
            IN employee_ids integer[],
            IN start_date date,
            IN end_date date,
            IN worked_hours numeric,
            IN worked_hours_operator text
        )
        RETURNS TABLE(employee_id integer, department_id integer, expected_working_hours double precision, holiday_hours double precision, absence_hours double precision, real_worked_hours double precision, total_hours double precision, difference double precision) AS
        $BODY$
            BEGIN
                Return Query
                
                with holidays as (
                    Select emp.id as employee_id, coalesce(count(pub_holidays.*),0) * min(shift.hours_per_day) as holiday_hours
                    from setu_hr_public_holidays pub_holidays, hr_employee emp, resource_calendar shift
                    where holiday_start_date::date >= start_date and holiday_start_date::date <= end_date and shift.id = emp.employee_attendance_report_working_hour_id
                    group by emp.id
                )
                Select data.* From
                (
                    Select  
                        attendance.employee_id, attendance.department_id,  
                        ((end_date - start_date) + 1)* attendance.hours_per_day as expected_worked_hours, 
                        coalesce(h.holiday_hours,0) as holiday_hours,
                        coalesce(leave.absence_hours,0) as absence_hours,
                        coalesce(attendance.real_worked_hours,0) as real_worked_hours,
                        coalesce(h.holiday_hours,0)  + coalesce(leave.absence_hours,0) + attendance.real_worked_hours as total,
                        (coalesce(h.holiday_hours,0) + coalesce(leave.absence_hours,0) + attendance.real_worked_hours) - (((end_date - start_date) + 1) * attendance.hours_per_day) as difference
                    From
                    (
                        Select 
                            D.employee_id,
                            D.department_id,
                            sum(D.real_worked_hours) as real_worked_hours,
                            max(D.hours_per_day) as hours_per_day
                        From(
                            Select 
                                att.employee_id,
                                emp.department_id,
                                sum(att.worked_hours) as real_worked_hours,
                                shift.hours_per_day
                            From 
                                hr_attendance att
                                    Inner Join hr_employee emp on emp.id = att.employee_id
                                    Left Join hr_department dept on dept.id = emp.department_id
                                    Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
                            where att.check_in::date >= start_date and att.check_in::date <= end_date and att.check_out::date >= start_date and att.check_out::date <= end_date
                            and 1 = case when array_length(department_ids,1) >= 1 then 
                                case when emp.department_id = ANY(department_ids) then 1 else 0 end
                                else 1 end 
                            and 1 = case when array_length(employee_ids,1) >= 1 then 
                                case when att.employee_id = ANY(employee_ids) then 1 else 0 end
                                else 1 end
                            Group by att.employee_id, emp.department_id, shift.hours_per_day
        
                            Union All
        
                            Select 
                                emp.id,
                                emp.department_id,
                                0 as real_worked_hours,
                                shift.hours_per_day
                            From  hr_employee emp 
                                Left Join hr_department dept on dept.id = emp.department_id
                                Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
                            where 1 = case when array_length(department_ids,1) >= 1 then 
                                case when emp.department_id = ANY(department_ids) then 1 else 0 end
                                else 1 end 
                            and 1 = case when array_length(employee_ids,1) >= 1 then 
                                case when emp.id = ANY(employee_ids) then 1 else 0 end
                                else 1 end
                            Group by emp.id, emp.department_id, shift.hours_per_day
                        )D
                        group by D.employee_id, D.department_id
                    )attendance
        
                    Left Join 
                    (
                        Select leave_data.employee_id, 
                            leave_data.hours_per_day,
                            sum(leave_data.leave_hours) as absence_hours 
                        From (
                            SELECT 
                                leave.employee_id, 
                                generate_series(date_from, date_to, '1 day'::interval) as leave_date,
                                case when leave.request_unit_hours then EXTRACT(EPOCH FROM (leave.date_to - leave.date_from))/3600 else  
                                    case when number_of_days > 1 then 1 else number_of_days end * shift.hours_per_day
                                end as leave_hours,
                                leave_type.request_unit,
                                shift.hours_per_day
                            from 
                                hr_leave leave
                                    Inner Join hr_leave_type leave_type on leave_type.id = leave.holiday_status_id
                                    Inner Join hr_employee emp on emp.id = leave.employee_id
                                    Left Join resource_calendar shift on shift.id = emp.employee_attendance_report_working_hour_id
                            where leave.state = 'validate' and date_from >= start_date
                            and 1 = case when array_length(department_ids,1) >= 1 then 
                                case when emp.department_id = ANY(department_ids) then 1 else 0 end
                                else 1 end 
                            and 1 = case when array_length(employee_ids,1) >= 1 then 
                                case when leave.employee_id = ANY(employee_ids) then 1 else 0 end
                                else 1 end
                        )leave_data
                        where leave_date >= start_date and leave_date <= end_date
                        Group by leave_data.employee_id, hours_per_day
                    )leave
                        on leave.employee_id = attendance.employee_id
                    Left Join holidays h on h.employee_id = attendance.employee_id
                    
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
    """
    cr.execute(qry)
