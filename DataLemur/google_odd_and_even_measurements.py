% sql:

with df_day as (
    select date(measurement_time) as measurement_day,
    row_number () over (partition by (date(measurement_time)) order by measurement_time asc) as rn,
    measurement_value
    from measurements
),

df_mes as (
    select measurement_day,
    sum(case when rn%2!=0 then measurement_value else 0 end ) as odd_sum,
    sum(case when rn%2=0 then measurement_value else 0 end ) as even_sum
    from df_day
    group by measurement_day
)

select 
measurement_day,
odd_sum,
even_sum
from df_mes