% pyspark

df_reviews = reviews

df_month = df_review.withColumn('month', f.month(f.col('submit_date')))

df_group = df_month.groupBy(f.col('month').alias('mnt'), f.col('product_id').alias('product')).agg(f.round(f.avg(f.col('stars')).alias('avg_stars'), 2)).sort('mnt', 'product', ascending=True)

% sql

with df_month as (
    select product_id, stars,
    extract (month from submit_date) as mnt
    from reviews
),
    
df_group as (
    select mnt, product_id as product,
    round(avg (stars), 2) as avg_stars
    from df_month
    group by (mnt, product_id)
    order by (mnt, product_id) asc
)

select * from df_group