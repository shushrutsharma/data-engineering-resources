% pyspark:

df_post = posts

df_post_2021 = df_post.filter(f.year(f.col('post_date')) == 2021)

df_user = (df_post_2021.groupBy('user_id')
           .agg(f.count('post_id').alias('post_count'),
                f.min('post_date').alias('first_post_date'),
                f.max('post_date').alias('latest_post_date')))

df_output = (df_user.filter(f.col('post_count') >= 2)
             .withColumn('days_between', f.datediff(f.col('latest_post_date'), f.col('first_post_date')))
             .select('user_id', 'days_between'))

df_output.show()

% sql:

with df_post_2021 as (
    select user_id, post_id, post_date
    from posts
    where extract(year from post_date) = 2021
),

df_user as (
    select user_id,
           date(min(post_date)) as first_post_date,
           date(max(post_date)) as latest_post_date
    from df_post_2021
    group by user_id
    having count(post_id) >= 2
)

select user_id, latest_post_date - first_post_date as days_between
from df_user