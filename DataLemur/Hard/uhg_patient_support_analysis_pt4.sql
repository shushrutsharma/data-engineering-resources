with df1 as (
    select
    extract (year from call_date) as yr,
    extract (month from call_date) as mnt,
    to_date(concat(extract (year from call_date), '-', extract (month from call_date)), 'yyyy-MM') as date,
    call_duration_secs
    from callers
),

df2 as (
    select
    yr, mnt, date,
    sum(case when call_duration_secs >= 300 then 1 else 0 end) as cnt
    from df1
    group by (yr, mnt, date)
)

SELECT 
    yr, 
    mnt,
    round((cnt - LAG(cnt, 1) OVER (ORDER BY date ASC))::numeric * 100.00 / 
    LAG(cnt, 1) OVER (ORDER BY date ASC), 1) AS long_calls_growth_pct
FROM df2
ORDER BY yr ASC, mnt ASC;