with df1 as (
    select
    merchant_id, credit_card_id, amount, transaction_timestamp,
    lag(transaction_timestamp, 1) over (partition by merchant_id, credit_card_id, amount order by transaction_timestamp asc) as prev
    from transactions
)

select
    sum(case when transaction_timestamp - prev <= INTERVAL '10 minutes' then 1 else 0 end) as payment_count
from df1
