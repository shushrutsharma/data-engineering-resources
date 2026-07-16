%pyspark:

df_messages = messages

df_aug22 = df_messages.filter(f.year(f.col('sent_date'))==2022).filter(f.month(f.col('sent_date'))==8)
df_users = df_aug22.groupBy('sender_id').agg(f.count_distinct('message_id').alias('message_count'))

df_output = df_users.sort('message_count', ascending=False).limit(2)

%sql:

with df_aug22 as (
    select sender_id, message_id
    from messages
    where extract (year from sent_date) = 2022 and extract (month from sent_date) = 8
),

df_users as (
    select sender_id,
    count (distinct message_id) as message_count
    from df_aug22
    group by sender_id
)

select * 
from df_users
order by message_count desc
limit 2
