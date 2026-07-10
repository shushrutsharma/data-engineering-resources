with df1 as (
    select
    extract (year from transaction_date) as year,
    product_id,
    spend as curr_year_spend,
    lag (spend) over (partition by(product_id) order by extract (year from transaction_date)) as prev_year_spend
    from user_transactions
)

select
    year,
    product_id,
    curr_year_spend,
    prev_year_spend,
    round((curr_year_spend-prev_year_spend)::numeric*100.00/prev_year_spend, 2)as yoy_rate
from
    df1
order by product_id asc, year asc