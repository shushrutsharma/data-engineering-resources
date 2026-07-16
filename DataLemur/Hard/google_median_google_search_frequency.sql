WITH cte1 AS (
    SELECT
        searches,
        num_users,
        SUM(num_users) OVER (ORDER BY searches) AS cum_users,
        SUM(num_users) OVER () AS total_users
    FROM search_frequency
),
cte2 AS (
    SELECT
        *,
        COALESCE(LAG(cum_users) OVER (ORDER BY searches), 0) AS prev_cum_users
    FROM cte1
)

SELECT round(AVG(searches), 1) AS median
FROM cte2
WHERE
    (prev_cum_users < FLOOR((total_users + 1) / 2.0)
     AND cum_users >= FLOOR((total_users + 1) / 2.0))
OR
    (prev_cum_users < CEIL((total_users + 1) / 2.0)
     AND cum_users >= CEIL((total_users + 1) / 2.0));