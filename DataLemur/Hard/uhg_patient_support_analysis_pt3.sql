with df1 as (
    select distinct on (policy_holder_id, date(call_date))
    policy_holder_id,
    call_date as end_date,
    date(call_date)-7 as start_date,
    lag (call_date, 1) over (partition by policy_holder_id order by call_date asc) as last_date
    from callers
),

df2 as (
select distinct
policy_holder_id
from df1
group by policy_holder_id
having max (case
        when last_date > start_date and
        last_date <= end_date 
        then 1 else 0 end) > 0
order by policy_holder_id asc
)

select count (distinct policy_holder_id) as policy_holder_count
from df2