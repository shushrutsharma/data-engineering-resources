%pyspark:



%sql:

with calls as (
    select policy_holder_id
    count (distinct case_id) as calls
    from callers
    group by policy_holder_id
)

select
count (distinct policy_holder_id) as policy_holder_count
from calls
where calls >2