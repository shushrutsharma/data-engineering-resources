with df as (
    select ticker, open,
    to_char(date, 'Mon-yyyy') as month,
    max (open) over (partition by ticker) as highest_open,
    min (open) over (partition by ticker) as lowest_open
    from stock_prices
),
    
high as (
    select distinct
    ticker, month as highest_mth, highest_open
    from df
    where open = highest_open
),

low as (
    select distinct
    ticker, month as lowest_mth , lowest_open
    from df
    where open = lowest_open
)

select distinct
    h.ticker, h.highest_mth, h.highest_open, l.lowest_mth, l.lowest_open
from high h
inner join low l
on h.ticker = l.ticker
order by ticker

# better way:

with df as (
    select ticker, open,
        to_char(date, 'Mon-yyyy') as month,
        max(open) over (partition by ticker) as highest_open,
        min(open) over (partition by ticker) as lowest_open
    from stock_prices
)

select
    ticker,
    max(case when open = highest_open then month end) as highest_mth,
    highest_open,
    max(case when open = lowest_open then month end) as lowest_mth,
    lowest_open
from df
group by ticker, highest_open, lowest_open
order by ticker