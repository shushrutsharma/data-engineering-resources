with df1 as (
    select
    item_type,
    sum (square_footage) as space
    from inventory
    group by item_type
),

df2 as (
    select
    item_type,
    space,
    round((floor(500000/space)), 0) item_count,
    lag (space) over (order by item_type desc) as prime_space,
    lag (round((floor(500000/space)), 0)) over (order by item_type desc) as prime_count
    from df1
    order by item_type desc
),

df3 as (
    select
    item_type,
    case
        when item_type = 'prime_eligible' then item_count
        when item_type = 'not_prime' then round((500000 - (prime_space*prime_count))/space, 0)
    end as item_count
    from df2
)

select
item_type,
item_count
from df3
order by item_count desc


-- ans2:

with prime as (
    select sum(square_footage) as prime_sqft
    from inventory
    where item_type = 'prime_eligible'
),
nonprime as (
    select sum(square_footage) as nonprime_sqft
    from inventory
    where item_type = 'not_prime'
),
calc as (
    select
        floor(500000 / prime_sqft) as prime_count,
        prime_sqft,
        nonprime_sqft
    from prime, nonprime
)
select 'prime_eligible' as item_type, prime_count as item_count
from calc
union all
select 'not_prime' as item_type,
       floor((500000 - prime_count * prime_sqft) / nonprime_sqft) as item_count
from calc

-- correct ans:

WITH summary AS (  
  SELECT  
    item_type,  
    SUM(square_footage) AS total_sqft,  
    COUNT(*) AS item_count  
  FROM inventory  
  GROUP BY item_type
),
prime_occupied_area AS (  
  SELECT  
    item_type,
    total_sqft,
    FLOOR(500000/total_sqft) AS prime_item_batch_count,
    (FLOOR(500000/total_sqft) * item_count) AS prime_item_count
  FROM summary  
  WHERE item_type = 'prime_eligible'
)

SELECT
  item_type,
  CASE 
    WHEN item_type = 'prime_eligible' 
      THEN (FLOOR(500000/total_sqft) * item_count)
    WHEN item_type = 'not_prime' 
      THEN FLOOR((500000 - (SELECT FLOOR(500000/total_sqft) * total_sqft FROM prime_occupied_area)) / total_sqft) * item_count
  END AS item_count
FROM summary
ORDER BY item_type DESC;
