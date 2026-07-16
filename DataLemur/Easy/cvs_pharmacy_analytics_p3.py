%pyspark:



%sql:

with sales as (
    select manufacturer,
    sum(total_sales) as total_sales
    from pharmacy_sales
    group by manufacturer
)

select manufacturer,
concat('$', round(total_sales / 1000000.0), ' million') as sales_mil
from sales
order by total_sales desc