
%pyspark:



%sql:

with multi as (
    select item_count,
    order_occurrences,
    item_count * order_occurrences as total_items
    from items_per_order
),
    
df_sum as (
    select
    sum (total_items) as sum_item,
    sum (order_occurrences) as sum_order
    from multi
)

select
round ((sum_item / sum_order)::numeric, 1) as mean
from df_sum