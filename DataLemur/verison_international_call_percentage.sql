select
  round((sum(case when coalesce(call_category, 'n/a') = 'n/a' then 1 else 0 end)::numeric/count(*))*100.0, 1) as uncategorised_call_pct
from
 callers

-- better :

select
    round(
        (sum(case when call_category is null or trim(call_category) in ('', 'n/a') then 1 else 0 end)::numeric
        / count(*)) * 100.0, 1
    ) as uncategorised_call_pct
from callers