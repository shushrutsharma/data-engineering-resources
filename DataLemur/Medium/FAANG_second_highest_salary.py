%pyspark:



%sql:

with sec as (
    select salary,
    rank (order by salary) as rn
    from employee
)
    
select
    distinct (salary) as second_highest_salary
from
    sec
where
    rn = 2