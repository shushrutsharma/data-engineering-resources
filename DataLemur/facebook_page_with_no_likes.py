% pyspark:

df_merger = pages.join(page_likes, ['page_id'], 'left').select(pages['page_id'], page_likes['user_id'])
df_empty = df_merger.filter(f.col('user_id').isNull()).select('page_id').dropDuplicates().sort(f.col('page_id'), ascending=True)

% sql:

with df_merger as (
    select pages.page_id, page_likes.user_id
    from pages
    left join page_likes
    on pages.page_id=page_likes.page_id
),
    
select distinct page_id
from df_merger
where user_id is NULL
order by page_id asc


