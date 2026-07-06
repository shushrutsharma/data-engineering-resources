%pyspark:



%sql:

with prof as (
    select drug,
    round(total_sales - cogs, 2) as total_profit
    from pharmacy_sales
)
    
select * 
from prof
order by total_profit desc
limit 3