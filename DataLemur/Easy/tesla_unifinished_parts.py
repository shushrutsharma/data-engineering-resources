% pyspark:

df_unfinished = parts_assembly.filter((f.col('finish_date').isNull())|(f.col('finish_date')=='')).select('part', 'assembly_step').dropDuplicates()

% sql:

with df_unfinished as (
    select part, assembly_step
    from parts_assembly
    where finish_date is NULL
)

select distinct part, assembly_step
from df_unfinished