with df1 as (
    select
    m.contact_id,
    m.event_type,
    extract(week from m.event_date) as week,
    extract(week from m.event_date) - row_number() over (partition by m.contact_id order by extract(week from m.event_date)) as gap,
    c.email
    from marketing_touches m
    inner join crm_contacts c
    on m.contact_id = c.contact_id
)

select distinct
email
from df1
group by email, gap
having
max(case when event_type = 'trial_request' then 1 else 0 end) > 0 and count (*) >=3