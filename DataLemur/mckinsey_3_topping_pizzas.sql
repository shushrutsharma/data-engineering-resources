with df1 as (
  select
  a.topping_name as t1,
  a.ingredient_cost as c1,
  b.topping_name as t2,
  b.ingredient_cost as c2
  from pizza_toppings a
  cross join pizza_toppings b
),

df2 as (
  select
  c.t1 as t1,
  c.c1 as c1,
  c.t2 as t2,
  c.c2 as c2,
  d.topping_name as t3,
  d.ingredient_cost as c3
  from df1 c
  cross join pizza_toppings d
)

SELECT DISTINCT
    (
        SELECT STRING_AGG(val, ',' ORDER BY val)
        FROM (
            VALUES (t.t1), (t.t2), (t.t3)
        ) AS x(val)
    ) AS pizza,
c1+c2+c3 as total_cost
FROM df2 t
where t1 != t2 and t1 != t3 and t2 != t3
order by total_cost desc, pizza asc