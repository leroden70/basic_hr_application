insert into dbo.absence_types
(absence_type, absence_description)
VALUES
('LEGAL', 'Legal holidays'),
('X-LEG', 'Xtra-legal holidays'),
('OVERT','Overtime recuperation'),
('SICK', 'Sickness absence')

insert into dbo.emp_holidays
(employee_id,start_date,end_date,absence_type,entitlement,balance)
select employee_id, hire_date, '9999-12-31', 'LEGAL', 20, 20 from dbo.employees

insert into dbo.emp_holidays
(employee_id,start_date,end_date,absence_type,entitlement,balance)
select employee_id, hire_date, '9999-12-31', 'X-LEG', 5, 5 from dbo.employees:


/////////////////////////////////////////////////////////////////////////////////////////////////////////////
    cur["employment_id"]
    cur["job_id"]
    cur["hire_date"]
    cur["department_id"]
select jh.employee_id,
	   jh.start_date,
	   jh.end_date,
	   jh.job_id,
	   jh.department_id
  from dbo.job_history jh
 where jh.employee_id = cur["employment_id"]
order by jh.start_date desc;
into prev["employee_id"], prev["start_date"], prev["end_date"], prev["job_id"], prev["department_id"];

if no record in job hierarchy

    insert into dbo.job_history (
        employee_id, start_date, end_date, job_id, department_id
    ) values (
        cur["employment_id"], prev["end_date"] + 1, CURRENT_DATE - 1, cur["job_id"], cur["department_id"]
    );

else

    insert into dbo.job_history (
        employee_id, start_date, end_date, job_id, department_id
    ) values (
        cur["employment_id"], cur["hire_date"], CURRENT_DATE - 1, cur["job_id"], cur["department_id"]
    );

UPDATE dbo.employees
   SET job_id = {new_job_id}
 WHERE employee_id = {cur_employee_id}