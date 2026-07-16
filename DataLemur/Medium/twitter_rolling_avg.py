%sql:

with r_avg as (
    select
        user_id,
        tweet_date,
        avg (tweet_count) over (partition by user_id order by tweet_date
                                rows between 2 preceding and current row) as rolling_avg_3rd
        from tweets

)
    
select user_id, tweet_date, round(rolling_avg_3d, 2) as rolling_avg_3d
from r_avg
order by user_id, tweet_date



%pyspark:

from pyspark.sql import Window
from pyspark.sql import functions as f

w = (
    Window
    .partitionBy("user_id")
    .orderBy("tweet_date")
    .rowsBetween(-2, 0)
)

result = (
    tweets_df
    .withColumn("rolling_avg_3d", f.round(f.avg("tweet_count").over(w), 2))
    .select("user_id", "tweet_date", "rolling_avg_3d")
)