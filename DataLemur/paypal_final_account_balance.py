% pyspark

df_trans = transactions.withColumn('bal_amount', when(f.col('transaction_type')=='Deposit', f.col('amount')).otherwise(f.col('amount')*-1))

df_final = df_trans.groupBy('account_id').agg(f.sum('bal_amount').alias('final_balance'))

% sql

with df_trans as (
with df_trans as (
    select account_id,
    case when transaction_type = 'Deposit' then amount
          else amount*-1 end as bal_amount
    from transactions
),
     
df_final as (
    select account_id,
    sum (bal_amount) as final_balance
    from df_trans
    group by account_id
)

select * from df_final