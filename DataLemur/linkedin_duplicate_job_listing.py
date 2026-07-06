%pyspark:

df_concat = job_listings.withColumn(
    'title_desc', f.concat_ws('-', f.col('title'), f.col('description'))
)

df_group = df_concat.groupBy('company_id').agg(
    f.count('job_id').alias('total_listings'),
    f.count_distinct('title_desc').alias('unique_listings')
)

df_output = (df_group.filter(f.col('total_listings') > f.col('unique_listings'))
             .agg(f.count('company_id').alias('duplicate_companies')))

###

w = Window.partitionBy('company_id', 'title', 'description').orderBy('job_id')

df_rank = job_listings.withColumn('rn', f.row_number().over(w))

df_dup_companies = df_rank.filter(f.col('rn') == 2).select('company_id').distinct()

df_output = df_dup_companies.agg(f.count('company_id').alias('duplicate_companies'))

%sql:

with df_rank as (
    select company_id, job_id,
           row_number() over (partition by company_id, title, description order by job_id) as rn
    from job_listings
),

df_dup_companies as (
    select distinct company_id
    from df_rank
    where rn = 2
)

select count(company_id) as duplicate_companies
from df_dup_companies

###

with df_concat as (
    select company_id, job_id,
           concat_ws('-', title, description) as title_desc
    from job_listings
),

df_group as (
    select company_id,
           count(job_id) as total_listings,
           count(distinct title_desc) as unique_listings
    from df_concat
    group by company_id
)

select count(company_id) as duplicate_companies
from df_group
where total_listings > unique_listings

