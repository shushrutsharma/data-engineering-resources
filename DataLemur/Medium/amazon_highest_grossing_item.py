%sql:

with df_2022 as (
    select category, product, spend
    from product_spend
    where extract (year from transaction_date) = 2022
),

df_gb as (
    select category, product,
    sum (spend) as total_spend
    from df_2022
    group by (category, product)
),

df_rank as (
    select category, product, total_spend,
    row_number () over (partition by (category) order by total_spend desc) as rn
    from df_gb
)

select category, product, total_spend
from df_rank
where rn < 3