%sql:

with df_join as (
    select employee.name, employee.salary, employee.department_id, department.department_name
    from employee
    inner join department
    on employee.department_id=department.department_id
),
    
df_final as (
    select department_name, name, salary,
    dense_rank () over (partition by department_name order by salary desc) as rn
    from df_join
)

select department_name, name, salary
from df_final
where rn <=3
order by department_name asc, salary desc, name asc