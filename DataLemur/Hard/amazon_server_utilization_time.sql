WITH sessions AS (
    SELECT
        server_id,
        status_time AS start_time,
        LEAD(status_time) OVER (
            PARTITION BY server_id
            ORDER BY status_time
        ) AS stop_time,
        session_status
    FROM server_utilization
)

SELECT
    FLOOR(
        SUM(EXTRACT(EPOCH FROM (stop_time - start_time))) / 86400
    ) AS total_uptime_days
FROM sessions
WHERE session_status = 'start';