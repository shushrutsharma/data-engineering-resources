with df1 as (
    select
        user_id,
        date(transaction_date) as t_date
    from
        transactions
),

df2 as (
    select user_id,t_date,
    lag (t_date, 2) over (partition by user_id order by t_date) as lag_date
    from df1
)

select distinct user_id
from df2
where
t_date-lag_date=2

## correct ans:

with df1 as (
    select distinct
        user_id,
        date(transaction_date) as t_date
    from transactions
),

df2 as (
    select
        user_id,
        t_date,
        lag(t_date, 2) over (partition by user_id order by t_date) as lag_date
    from df1
)

select distinct user_id
from df2
where t_date - lag_date = 2
order by user_id