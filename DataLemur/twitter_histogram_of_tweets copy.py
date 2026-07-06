df_2022 = df_tweet.withColumn('year', f.substring(f.col('tweet_date'), 7,10)).filter(f.col('year')=='2022')
gb_user = df_2022.groupBy('user_id').agg(f.count_distinct('tweet_id').alias('unique_tweets'))
gb_twt = gb_user.groupBy('unique_tweets').agg(f.count('user_id').alias('user_count'))
df_final = gb_twt.select(f.col('unique_tweets').alias('tweet_bucket'), f.col('user_count').alias('user_num'))

%sql

with df_2022 as (
    select
    tweet_id, user_id
    from tweets
    where extract(year from tweet_date) = 2022
),
    
gb_user as (
    select user_id, count_distinct('tweet_id') as unique_tweets
    from df_2022
    group by user_id
),

gb_twt as (
    select unique_tweets, count_distinct('user_id') as user_count
    from gb_ser
    group by gb_twt
),

df_final as (
    select unique_tweets as tweet_bucket, user_count as users_num
    from gb_twt
)

select * from df_final


## correct ans: 

WITH per_user AS (                              -- = df_2022 + gb_user
    SELECT
        user_id,
        COUNT(DISTINCT tweet_id) AS unique_tweets
    FROM tweets
    WHERE EXTRACT(YEAR FROM tweet_date) = 2022  -- = your .filter()
    GROUP BY user_id                            -- = your .groupBy('user_id')
)
SELECT                                          -- = gb_twt + df_final
    unique_tweets      AS tweet_bucket,
    COUNT(user_id)     AS users_num
FROM per_user
GROUP BY unique_tweets;


with df_2022 as (
    select tweet_id, user_id
    from tweets
    where extract(year from tweet_date) = 2022
),

gb_user as (
    select user_id, count(distinct tweet_id) as unique_tweets
    from df_2022
    group by user_id
),

gb_twt as (
    select unique_tweets, count(user_id) as user_count
    from gb_user
    group by unique_tweets
),

df_final as (
    select unique_tweets as tweet_bucket, user_count as users_num
    from gb_twt
)

select * from df_final


## trying to map my CTEs into nested manner:


with df_2022 as (
    select tweet_id, user_id
    from tweets
    where extract(year from tweet_date) = 2022
),

gb_user as (
    select user_id, count(distinct tweet_id) as unique_tweets
    from df_2022
    group by user_id
),

gb_twt as (
    select unique_tweets, count(user_id) as user_count
    from gb_user
    group by unique_tweets
),

df_final as (
    select unique_tweets as tweet_bucket, user_count as users_num
    from gb_twt
)


select * from (
    select unique_tweets as tweet_bucket, user_count as users_num
    from (
    select unique_tweets, count(user_id) as user_count
    from (
    select user_id, count(distinct tweet_id) as unique_tweets
    from (
    select tweet_id, user_id
    from tweets
    where extract(year from tweet_date) = 2022
) as df_2022
    group by user_id
) as gb_user
    group by unique_tweets
) as gb_twt
) as df_final