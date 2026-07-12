with df1 as (
    select distinct
    user_id,
    login_date,
    extract (month from login_date) as mnt
    from user_logins
),

df2 as (
    select
    mnt,
    login_date as curr,
    lag(login_date, 1) over (partition by user_id order by login_date asc) as prev
    from df1
)

select
mnt,

sum(case when (extract(month from curr)- extract(month from prev) > 1 and extract(year from curr) = extract(year from prev)) or prev is NULL then 1 else 0 end) as reactivated_users

from df2
group by mnt
having
sum(case when (extract(month from curr)- extract(month from prev) > 1 and extract(year from curr) = extract(year from prev)) or prev is NULL then 1 else 0 end) > 0
order by mnt asc
