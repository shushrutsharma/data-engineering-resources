with df_sales as (
    select product_id,
    sum (coalesce(sales_quantity, 0)) as total_sales,
    max (coalesce(rating, 0)) as max_rating
    from product_sales
    group by product_id
),

df_join as (
    select
    s.product_id, s.total_sales, s.max_rating, p.product_name, p.category_name,
    max(total_sales) over (partition by category_name) as best_sales,
    max(max_rating) over (partition by category_name) as best_rating
    from df_sales s
    inner join products p
    on s.product_id = p.product_id
),

df_best1 as (
    select
        category_name, product_name, total_sales, best_sales, max_rating, best_rating,
        count(*) over(partition by category_name) as cnt
    from
        df_join
    where
        total_sales = best_sales
),

df_best2 as (
    select
    category_name, product_name, cnt
    from
    df_best1
    where
    (cnt = 1 and total_sales = best_sales) or
    (cnt > 1 and max_rating = best_rating)
)

select category_name, product_name from df_best2 order by category_name asc

-- better version:

with sales_agg as (
    select
        product_id,
        sum(coalesce(sales_quantity, 0)) as total_sales,
        max(coalesce(rating, 0)) as max_rating
    from product_sales
    group by product_id
),

ranked as (
    select
        p.category_name,
        p.product_name,
        row_number() over (
            partition by p.category_name
            order by s.total_sales desc, s.max_rating desc
        ) as rn
    from sales_agg s
    inner join products p on s.product_id = p.product_id
)

select category_name, product_name
from ranked
where rn = 1
order by category_name asc