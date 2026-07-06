%pyspark:



%sql:

with df_q3 as (
    select employee_id, query_id
    from queries
    where date(query_starttime)>=to_date('01-07-2023', 'dd-MM-yyyy') and date(query_starttime)<=to_date('30-09-2023', 'dd-MM-yyyy')
),
    
df_join as (
    select employees.employee_id, df_q3.query_id
    from employees
    left join df_q3
    on employees.employee_id=df_q3.employee_id
),

df_emp_gb as (
    select employee_id,
    count (distinct query_id) as unique_queries
    from df_join
    group by employee_id
)

select unique_queries,
count (distinct employee_id) as employee_count
from df_emp_gb
group by unique_queries