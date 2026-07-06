% pyspark:

df_trades = trades
df_users = users

df_completed = df_trades.filter(f.col('status')=='Completed').select('user_id', 'order_id')
df_join = df_completed.join(df_users, ['user_id'], 'inner').select(df_completed['*'], df_users['city'])

df_output = df_join.groupBy('city').agg(f.count_distinct('order_id').alias('total_orders')).sort('total_order', ascending=False).limit(3)

df_output.show()


% sql:

with df_completed as (
    select user_id, order_id
    from trades
    where status = 'Completed'
),
    
df_join as (
    select df_completed.user_id, df_completed.order_id, users.city
    from df_completed
    left join users
    on df_completed.user_id = users.user_id
)

select city,
count (distinct order_id) as total_order
from df_join
group by city
order by total_order desc
limit 3