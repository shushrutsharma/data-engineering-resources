%pyspark

skills = ['Python', 'Tableau', 'PostgreSQL']
df_skills = candidates.filter(f.lower(f.col('skills')).isin(skills.lower()))
df_output = df_skill.select('candidate_id').sort(f.col('candidate_id').asc()).limit(1)

df_output.show()


%sql

with df_skills as (
    select candidate_id, skill
    from candidates
    where skill = 'Python' and skill = 'Tableau' and skill = 'PostgreSQL'
),
    
df_output as (
    select candidate_id
    from df_skill
    order by candidate_id asc()
    limit 1
)

select * from df_output

## ------
## using windowPartitionBy
## ------

skills = ['Python', 'Tableau', 'PostgreSQL']
lower_skills = [item.lower() for item in skills]

w = Window.partitionBy("candidate_id")

df_skills = candidates.filter(f.lower(f.col('skill')).isin(lower_skills))
df_skills_all_three = df_skills.withColumn('skill_count', f.count(f.col('skill')).over(w)).filter(f.col('skill_count')==3).drop('skill_count')

df_output = df_skills_all_three.select('candidate_id').dropDuplicates().sort(f.col('candidate_id').asc())

df_output.show()

%% sql 

with df_skills as (
    select candidate_id, skill
    from candidates
    where skill in ('Python', 'Tableau', 'PostgreSQL')
),

df_skills_all_three as (
    select candidate_id
    from df_skill
    where count(skill) over (partition by candidate_id) = 3
),

select distinct candidate_id
from df_skills_all_three
order by candidate_id asc
