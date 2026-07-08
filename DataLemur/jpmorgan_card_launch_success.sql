with df_month as (
    select card_name, issued_amount,
    row_number () over (partition by card_name order by to_date(concat(issue_month, '-', issue_year), 'MM-YYYY') asc) as rn
    from monthly_cards_issued
)

select card_name, issued_amount
from df_month
where rn = 1
order by issued_amount desc