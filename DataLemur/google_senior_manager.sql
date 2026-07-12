WITH cte AS (
  
  SELECT
    t1.manager_name AS manager_name,                -- name of sr. mgr candidate
    t1.manager_id AS manager_id,                    -- id of sr. mgr candidate
    COUNT (DISTINCT t1.emp_id) AS direct_reportees, -- no. of direct reportees
    
    -- no. of reportees for indirect reportees of sr. mgr candidates
    COUNT(DISTINCT t3.emp_id) AS reportees_of_indirect_reportees       
  
  FROM employees t1
  
  -- get all managers whose employees are managers (senior manager candidates)
  INNER JOIN employees t2
    ON t1.emp_id = t2.manager_id
  
  -- get all senior manager candidates 
  -- along with direct reports of low level managers
  LEFT JOIN employees t3
    ON t2.emp_id = t3.manager_id
  
  GROUP BY 1, 2
)

SELECT
  manager_name,
  direct_reportees
FROM cte

-- senior managers cannot have indirect reportees who are also managers
-- only direct reportees can be managers;
WHERE reportees_of_indirect_reportees = 0

-- claude:

WITH managers AS (
  SELECT DISTINCT manager_id
  FROM employees
),

candidates AS (
  SELECT
    manager_id,
    manager_name,
    COUNT(DISTINCT emp_id) AS direct_reportees
  FROM employees
  WHERE emp_id IN (SELECT manager_id FROM managers)   -- keep only reports who are themselves managers
  GROUP BY manager_id, manager_name
)

SELECT
  manager_name,
  direct_reportees
FROM candidates c
WHERE NOT EXISTS (
  SELECT 1
  FROM employees e
  WHERE e.manager_id = c.manager_id                    -- e = a direct report of c
    AND e.emp_id IN (SELECT manager_id FROM candidates) -- and that report is itself a candidate
)
ORDER BY direct_reportees DESC;