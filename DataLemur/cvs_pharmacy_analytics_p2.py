%pyspark:



%sql:

with prof as (
    select manufacturer, product_id,
    round(total_sales - cogs, 2) as total_profit
    from pharmacy_sales
),
    
losses as (
    select manufacturer,
    count (product_id) as drug_count,
    sum (total_profit) as total_loss
    from prof
    where total_profit < 0
    group by manufacturer
)

select manufacturer,
drug_count,
abs (total_loss) as total_loss
from losses
order by total_loss desc
