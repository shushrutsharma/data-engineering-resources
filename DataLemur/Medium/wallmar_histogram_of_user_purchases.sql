with df1 as (
    select
    user_id, product_id,
    date(transaction_date) as t_date
    from user_transactions
),

df2 as (
    select t_date, user_id,
    count (*) over (partition by user_id, t_date) as purchase_count,
    max (t_date) over (partition by user_id) as max_date
    from df1
)

select DISTINCT
      t_date,
      user_id,
      purchase_count
from df2
where t_date = max_date
order by t_date asc


-- better method:

with product_counts as (
    select
        user_id,
        transaction_date,
        count(distinct product_id) as purchase_count
    from user_transactions
    group by user_id, transaction_date
),

ranked as (
    select
        user_id,
        transaction_date,
        purchase_count,
        rank() over (partition by user_id order by transaction_date desc) as rn
    from product_counts
)

select transaction_date, user_id, purchase_count
from ranked
where rn = 1
order by transaction_date asc