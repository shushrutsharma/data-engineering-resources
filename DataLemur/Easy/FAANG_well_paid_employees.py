% pyspark

df_emp = employee

df_man = df_emp.select(f.col('employee_id'), f.col('salary').alias('manager_salary'), f.col('department_id'))

df_final = df_emp.join(df_man, (df_emp.manager_id=df_man.employee_id)&(df_emp.salary>df_man.manager_salary), 'inner').select(df_emp['employee_id'], df_emp['name'].alias('employee_name')).dropDuplicates()

% sql

with df_man as (
    select employee_id, department_id,
    salary as manager_salary
    from employee
),

df_final as (
    select employee.employee_id,
    employee.name as employee_name
    from employee
    inner join df_man
    on (employee.manager_id=df_man.employee_id) and (employee.salary>df_man.manager_salary)
)

select * from df_final