with df_month as (
    select user_id, event_date,
    extract(month from event_date) as e_month
    from user_actions
    where
    (extract(month from event_date) = 7 or
     extract(month from event_date) = 6) and
    (extract(year from event_date) = 2022)       
),

df_active as (
    select user_id,
    count (distinct (e_month)) as no_month
    from df_month
    group by user_id
    having count (distinct (e_month)) > 1
),

df_join as (
    select
    m.user_id, m.e_month
    from df_month m
    inner join df_active a
    on m.user_id = a.user_id
)

select
    max (e_month) as month,
    count (distinct user_id) as monthly_active_users
from df_join

-- better way:

with monthly as (
    select
        user_id,
        max(case when extract(month from event_date) = 7 then 1 else 0 end) as in_july,
        max(case when extract(month from event_date) = 6 then 1 else 0 end) as in_june
    from user_actions
    where extract(year from event_date) = 2022
      and extract(month from event_date) in (6, 7)
    group by user_id
)
select
    7 as month,
    count(*) as monthly_active_users
from monthly
where in_july = 1 and in_june = 1