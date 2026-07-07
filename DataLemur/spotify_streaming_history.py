% sql:

with df_week as (
    select user_id, song_id,
    count (*) as song_plays
    from songs_weekly
    where listen_time < to_date('05-08-2022', 'dd-MM-yyyy')
    group by user_id, song_id
),
    
df_full as (
    select user_id, song_id, song_plays
    from songs_history
    union
    select user_id, song_id, song_plays
    from df_week
) ,

full_gb as (
    select user_id, song_id,
    sum (song_plays) as song_plays
    from df_full
    group by user_id, song_id
)

select *
from full_gb
order by song_plays desc
