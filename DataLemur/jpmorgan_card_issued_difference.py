%pyspark:



%sql:

with df_group as (
    select card_name,
    max (issued_amount) as best,
    min (issued_amount) as worst
    from monthly_cards_issued
    group by card_name
)

select card_name,
(best - worst) as difference
from df_group
order by difference desc