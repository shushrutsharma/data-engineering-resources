% pyspark:

mobile = ['phone', 'tablet']

df_format = viewership.withColumn('type', when(f.col('device_type')=='laptop', f.lit('laptop')).\
                                            when(f.col('device_type').isin(mobile), f.lit('mobile')).otherwise(f.lit('Others')))

df_output = (df_format.groupBy()
             .pivot('type')
             .agg(f.count('user_id'))
             .withColumnRenamed('laptop', 'laptop_views')
             .withColumnRenamed('mobile', 'mobile_views'))

df_output.show()

% sql:

select
    count(case when device_type = 'laptop' then 1 end) as laptop_views,
    count(case when device_type in ('tablet', 'phone') then 1 end) as mobile_views
from viewership


## ------

WITH df_format AS (
    SELECT 
        user_id,
        CASE 
            WHEN device_type = 'laptop' THEN 'laptop'
            WHEN device_type IN ('phone', 'tablet') THEN 'mobile'
            ELSE 'Others'
        END AS type
    FROM viewership
)

SELECT 
    laptop AS laptop_views,
    mobile AS mobile_views,
    Others
FROM df_format
PIVOT (
    COUNT(user_id)
    FOR type IN ('laptop', 'mobile')
);


WITH df_format AS (
    SELECT 
        user_id,
        CASE 
            WHEN device_type = 'laptop' THEN 'laptop'
            WHEN device_type IN ('phone', 'tablet') THEN 'mobile'
            ELSE 'Others'
        END AS type
    FROM viewership
)

SELECT 
    laptop AS laptop_views,
    mobile AS mobile_views
FROM df_format
PIVOT (
    COUNT (user_id)
    FOR type IN ('laptop', 'mobile')
)