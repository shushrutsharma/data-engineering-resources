%pyspark:



%sql:

with sec as (
    select salary,
    rank () over (order by salary desc) as rn
    from employee
)
    
select
    distinct (salary) as second_highest_salary
from
    sec
where
    rn = 2