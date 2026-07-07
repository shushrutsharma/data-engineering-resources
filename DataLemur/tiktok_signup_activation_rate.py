%sql:

with df_join as (
    select emails.email_id, emails.user_id,
    coalesce (texts.signup_action, 'NA') as signup_action
    from emails
    left join texts
    on emails.email_id=texts.email_id
),
    
df_rate as (
    select
    count (case when signup_action = 'Confirmed' then 1 end) as confirm_num,
    count (case when signup_action <> 'Confirmed' then 1 end) as not_confirm_num
    from df_join
)

select
    round (confirm_num::numeric / (confirm_num+not_confirm_num), 2) as confirm_rate
from df_rate

##

with df_join as (
    select emails.email_id, emails.user_id,texts.signup_action
    from emails
    left join texts
    on emails.email_id=texts.email_id
),
    
df_rate as (
    select
    count (case when signup_action = 'Confirmed' then 1 end) as confirm_num,
    count (case when signup_action <> 'Confirmed' then 1 end) as not_confirm_num
    from df_join
)

select
    round (confirm_num::numeric / (confirm_num+not_confirm_num), 2) as confirm_rate
from df_rate



## better:

with user_status as (
    select e.email_id,
    max(case when t.signup_action = 'Confirmed' then 1 else 0 end) as confirmed
    from emails e
    left join texts t on e.email_id = t.email_id
    group by e.email_id
)
select round(sum(confirmed)::numeric / count(*), 2) as confirm_rate
from user_status
