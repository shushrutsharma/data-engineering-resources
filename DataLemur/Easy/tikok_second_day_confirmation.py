%pyspark:



%sql:

with df_confirm as (
    select email_id, action_date
    from texts
    where signup_action = 'Confirmed'
),
    
df_join as (
    select emails.user_id,emails.signup_date,df_confirm.action_date
    from emails
    inner join df_confirm
    on emails.email_id = df_confirm.email_id and DATE(df_confirm.action_date)-DATE(emails.signup_date) = 1
)

select distinct user_id
from df_join