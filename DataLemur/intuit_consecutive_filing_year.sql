with df1 as (
    select distinct
    user_id,
    extract(year from filing_date) as year,
    lag (extract(year from filing_date), 2) over (partition by user_id order by (extract(year from filing_date))) as last_2year
    from filed_taxes
    where product like '%TurboTax%'
)

select distinct
    user_id
from
    df1
where
    year-last_2year =2
order by user_id