%pyspark:



%sql:

with df_filter as (
    select user_id, activity_type, time_spent
    from activities
    where activity_type in ('open', 'send') 
),

df_join as (
    select df_filter.user_id, df_filter.activity_type, df_filter.time_spent,
    coalesce (age_breakdown.age_bucket, 'unknown') as age_bucket
    from df_filter
    left join age_breakdown
    on df_filter.user_id=age_breakdown.user_id
),

df_gb as (
    select age_bucket,
    sum (time_spent) as total_time_spent,
    sum (case when activity_type = 'open' then time_spent else 0 end) as open_time,
    sum (case when activity_type = 'send' then time_spent else 0 end) as send_time,
    round ((send_time *100.0) /total_time_spent, 2) as send_perc,
    round ((open_time *100.0) /total_time_spent, 2) as open_perc
    from df_join
    group by age_bucket
)

select age_bucket, send_perc, open_perc
from df_gb

####


with df_filter as (
    select user_id, activity_type, time_spent
    from activities
    where activity_type in ('open', 'send') 
),

df_join as (
    select df_filter.user_id, df_filter.activity_type, df_filter.time_spent,
    coalesce (age_breakdown.age_bucket, 'unknown') as age_bucket
    from df_filter
    left join age_breakdown
    on df_filter.user_id=age_breakdown.user_id
),

df_gb as (
    select age_bucket,
    sum (time_spent) as total_time_spent,
    sum (case when activity_type = 'open' then time_spent else 0 end) as open_time,
    sum (case when activity_type = 'send' then time_spent else 0 end) as send_time,
    from df_join
    group by age_bucket
)

select age_bucket,
    round ((send_time *100.0) /total_time_spent, 2) as send_perc,
    round ((open_time *100.0) /total_time_spent, 2) as open_perc
from df_gb
