with df1 as (
    select
    a.user_id, a.status as old_status,
    coalesce(d.paid, 0) as paid,
    d.user_id as new_user,
    case
        when a.user_id is NULL then d.user_id
        else a.user_id
    end as final_user_id
    from advertiser a
    full join daily_pay d
    on a.user_id = d.user_id
)

select final_user_id as user_id,
case
    when old_status = 'NEW' and paid > 0 then 'EXISTING'
    when old_status = 'NEW' and paid = 0 then 'CHURN'
    when old_status = 'EXISTING' and paid > 0 then 'EXISTING'
    when old_status = 'EXISTING' and paid = 0 then 'CHURN'
    when old_status = 'CHURN' and paid > 0 then 'RESURRECT'
    when old_status = 'CHURN' and paid = 0 then 'CHURN'
    when old_status = 'RESURRECT' and paid > 0 then 'EXISTING'
    when old_status = 'RESURRECT' and paid = 0 then 'CHURN'
    else 'NEW'
end as new_status
from df1
order by final_user_id