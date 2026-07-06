% pyspark

df_events = events

df_events_2022 = df_events.filter(f.year(f.col('timestamp'))==2022)

df_gb  = df_events_2022.groupBy('app_id').agg(f.count(when(f.col('event_type')=='impression', 1)).alias('imp_count'), f.count(when(f.col('event_type')=='click', 1)).alias('click_count')).withColumn('ctr', f.round((f.col('click_count')*100.00)/f.col('imp_count'), 2))

% sql

with df_events_2022 as (
    select app_id, event_type
    from events
    where extract(year from timestamp)=2022
),

df_gb as (
    select app_id,
    count (case when event_type = 'impression' then 1 end) as imp_count,
    count (case when event_type = 'click' then 1 end) as click_count
    from df_events_2022
    group by app_id
)

select app_id,
round((click_count *100.00)/imp_count, 2) as ctr
from df_gb