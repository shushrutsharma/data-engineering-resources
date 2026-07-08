select
    round((sum(case when call_category = 'n/a' then 1 else 0)::numeric/count(*))*100.0, 1) as uncategorised_call_pct
from
 callers