% sql:

with dis_cat as (
    select count (distinct product_category) as dis_cat
    from products
),

df_join as (
    select c.customer_id, c.product_id, p.product_category
    from customer_contracts c
    left join products p
    on c.product_id=p.product_id
),

df_cj as (
    select j.customer_id, d.dis_cat
    from df_join j
    cross join dis_cat d
    group by customer_id, dis_cat
    having count (distinct product_category) = dis_cat
)

select customer_id from df_cj

##-------

## quicker:

select c.customer_id
from customer_contracts c
join products p on c.product_id = p.product_id
group by c.customer_id
having count(distinct p.product_category) = (select count(distinct product_category) from products)


% pyspark:

from pyspark.sql import functions as f

# Join contracts with products
df_join = customer_contracts.join(products, on="product_id", how="inner")

# Get total distinct category count as a Python scalar (equivalent to the scalar subquery)
total_categories = products.select(f.countDistinct("product_category")).collect()[0][0]

# Group by customer, compare against the scalar
result = (
    df_join.groupBy("customer_id")
    .agg(f.countDistinct("product_category").alias("category_count"))
    .filter(f.col("category_count") == total_categories)
    .select("customer_id")
)

result.show()