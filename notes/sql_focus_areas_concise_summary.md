# SQL Focus Areas — Concise Summary

> **Purpose:** A compact revision sheet of the recurring mistakes, edge cases, and reusable SQL patterns documented in `sql_focus_areas.md`.
>
> Use this:
>
> - Before submitting a query.
> - Before SQL interviews or mock interviews.
> - To quickly recall recurring weak areas.
> - To identify whether a mistake is new or repeated.
>
> **Detailed source:** `notes/sql_focus_areas.md`  
> **Source log last updated:** 12 Jul 2026

---

## Current Status

- Completed all free DataLemur Easy, Medium, and Hard SQL questions.
- SQL fundamentals and advanced patterns are now at maintenance level.
- Window-function fluency has improved significantly.
- Typos and alias-name drift have reduced after stopping the PySpark-first scaffold.
- Strong at detecting hidden correctness issues in both personal and official solutions.
- Main remaining gap: catching known edge cases before the first submission rather than during review.
- Next practice source: LeetCode SQL 50, followed by selected StrataScratch questions.
- SQL should remain a daily maintenance activity, not replace higher-priority Data Engineering preparation.

---

# Pre-Submit Checklist

## Grain and transformation order

- Define what one row represents at every CTE and in the final output.
- Watch for functions such as `DATE()`, `DATE_TRUNC()`, or concatenation silently changing the grain.
- Deduplicate before windowing when row position must represent a real sequence.
- Aggregate to the required business grain before applying `LAG`, `RANK`, or other windows.
- Raw transactions are not equivalent to monthly, yearly, product-level, or user-level totals.

## Duplicates and overproduction

- Use `DISTINCT` only when the exact duplicate source can be named.
- A trailing `DISTINCT` usually indicates an incorrect upstream grain or join fan-out.
- Prefer constraining row generation at source rather than generating extra rows and removing them later.
- Avoid aggregate-then-join-back patterns when conditional aggregation can solve the problem directly.
- Avoid dead CTEs, pass-through CTEs, and windows when a normal `GROUP BY` is sufficient.

## Joins

- Anchor the query on the table that defines the valid output entities.
- Use `LEFT JOIN` when entities with no activity must still appear.
- Avoid `FULL JOIN` when a transaction, payment, event, or lookup table can introduce phantom entities.
- Check whether one-to-many joins multiply rows before aggregating.
- Use strict-inequality self-joins such as `a < b < c` to generate unique combinations without permutations or `DISTINCT`.

## NULLs and zero preservation

- Treat `NULL`, empty strings, and whitespace as different values unless normalized explicitly.
- Do not use `COALESCE` inside `COUNT(DISTINCT ...)` when NULLs are meant to count as zero.
- Do not filter out legitimate zero-count groups using `HAVING aggregate > 0`.
- Preserve entities or periods whose correct result is zero.
- Use `NULLIF(denominator, 0)` in ratios and growth calculations.
- Growth from a zero base should normally return `NULL`, not raise an error or invent a percentage.

## Aggregation semantics

- `COUNT(CASE WHEN ... THEN 1 END)` requires the false branch to remain `NULL`.
- `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` requires an explicit zero.
- Never use `COUNT(CASE WHEN ... THEN 1 ELSE 0 END)`.
- “At least N” means `HAVING COUNT(...) >= N`.
- “Has all N values” usually means `HAVING COUNT(DISTINCT value) = N`.
- Encode the written requirement, not the appearance of the sample output.

## Ranking and ordering

- Use `RANK` when all tied rows must survive.
- Use `ROW_NUMBER` when exactly one winner is required.
- Encode primary ranking and tie-break logic in one composite `ORDER BY`.
- Do not calculate a maximum, filter, calculate another maximum, and filter again when one ranking pass works.
- Every ordering-dependent window should have a deterministic sort.
- Append a primary key when timestamps or business ordering columns can tie.
- `DISTINCT ON` requires an `ORDER BY` beginning with the same distinct key.
- Add every output ordering or formatting rule explicitly, even when the sample contains no ties.
- Sort using the unrounded aggregate, not the rounded display value.

## Mathematical correctness

- Cast an operand to numeric before division.
- Casting after integer division cannot recover the lost decimals.
- Use `FLOOR` for physical counts such as batches, seats, items, or full days.
- Do not use `ROUND` when rounding upward could exceed capacity.
- Pay attention to strict wording such as `> 300` versus `>= 300`.

## SQL syntax and hygiene

- Write `GROUP BY a, b`, not `GROUP BY (a, b)`.
- Re-read every CTE, alias, and column name before submission.
- Check for singular/plural drift and names copied from earlier questions.
- Prefer direct sorting on existing year and month columns over rebuilding dates through strings.
- Use `UNION ALL` when duplicate rows are meaningful.
- Use `UNION` only when deduplication is part of the requirement.

---

# Keeper Patterns

## 1. Aggregate before windowing

Use when the prompt asks for totals by a particular period or entity.

```sql
WITH yearly AS (
    SELECT
        product_id,
        EXTRACT(YEAR FROM transaction_date) AS year,
        SUM(spend) AS total_spend
    FROM transactions
    GROUP BY product_id, EXTRACT(YEAR FROM transaction_date)
)
SELECT
    product_id,
    year,
    total_spend,
    LAG(total_spend) OVER (
        PARTITION BY product_id
        ORDER BY year
    ) AS previous_spend
FROM yearly;
```

---

## 2. Deduplicate before sequence windows

Use when multiple events can occur on the same day but the logic depends on distinct days.

```sql
WITH user_days AS (
    SELECT DISTINCT
        user_id,
        DATE(transaction_date) AS transaction_day
    FROM transactions
)
SELECT
    user_id,
    transaction_day,
    LAG(transaction_day) OVER (
        PARTITION BY user_id
        ORDER BY transaction_day
    ) AS previous_day
FROM user_days;
```

---

## 3. Conditional aggregation instead of join-back logic

Use when testing several conditions for the same entity.

```sql
WITH user_flags AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_month = 6 THEN 1 ELSE 0 END) AS active_june,
        MAX(CASE WHEN event_month = 7 THEN 1 ELSE 0 END) AS active_july
    FROM activity
    GROUP BY user_id
)
SELECT COUNT(*)
FROM user_flags
WHERE active_june = 1
  AND active_july = 1;
```

---

## 4. Event logs to sessions using `LEAD`

Use when start and stop events appear in chronological order.

```sql
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
        SUM(EXTRACT(EPOCH FROM stop_time - start_time)) / 86400
    ) AS total_uptime_days
FROM sessions
WHERE session_status = 'start';
```

---

## 5. Membership tests

- SQL `IN (subquery)` maps conceptually to a PySpark `left_semi` join.
- SQL `NOT EXISTS` maps conceptually to a PySpark `left_anti` join.
- Use membership constructs when the right side is only used to test existence.
- Avoid an inner join followed by `DISTINCT` when no right-side columns are required.

---

## 6. Correlated `NOT EXISTS`

Read it as: keep the current outer row only when no matching inner row exists.

```sql
SELECT c.manager_id
FROM candidates c
WHERE NOT EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.manager_id = c.manager_id
      AND e.emp_id IN (
          SELECT manager_id
          FROM candidates
      )
);
```

---

## 7. Preserve zero-count entities with `LEFT JOIN`

Use the valid entity list as the anchor.

```sql
SELECT
    e.entity_id,
    COUNT(a.activity_id) AS activity_count
FROM entities e
LEFT JOIN activity a
    ON e.entity_id = a.entity_id
GROUP BY e.entity_id;
```

---

## 8. Unique combinations using strict inequalities

Use when combinations are unordered and repeated selections are not allowed.

```sql
SELECT
    a.name,
    b.name,
    c.name
FROM items a
JOIN items b
    ON a.name < b.name
JOIN items c
    ON b.name < c.name;
```

This produces each three-item combination exactly once.

---

## 9. Deterministic ordered windows

Always append a unique key when the business ordering column can tie.

```sql
LAG(transaction_timestamp) OVER (
    PARTITION BY merchant_id, credit_card_id, amount
    ORDER BY transaction_timestamp, transaction_id
)
```

---

## 10. Gap-filled period analysis

- Grouping existing rows only returns periods present in the data.
- Missing months can cause `LAG` to compare non-adjacent periods.
- Generate the complete calendar first.
- `LEFT JOIN` the calculated activity to the calendar.
- Convert missing counts to zero only where that matches the business definition.

---

## 11. Weighted median from a frequency table

- Do not expand billions of logical rows.
- Calculate cumulative frequencies.
- Find the bucket containing the middle position or positions.
- For an odd population, both median positions are identical.
- For an even population, average the values containing the two middle positions.

---

## 12. Boundary rows with `LEAD`, `LAG`, and `COALESCE`

Use explicit neighbour logic for endpoint rows rather than relying on odd/even IDs or maximum-value overrides.

```sql
COALESCE(
    LEAD(value) OVER (ORDER BY id),
    value
)
```

---

# Recurring Failure Patterns

- Thinking in PySpark first and translating mechanically into SQL.
- Losing track of row grain after date conversion, grouping, or joins.
- Windowing raw rows when the prompt asks for totals.
- Adding `DISTINCT` reflexively.
- Generating excess rows and pruning them later.
- Joining aggregated data back to detail unnecessarily.
- Using the wrong output anchor table.
- Filtering out zero-count entities or periods.
- Ignoring missing calendar periods.
- Using nondeterministic ordering in windows.
- Missing explicit tie-handling or output ordering requirements.
- Inferring requirements from the sample output.
- Over-building solutions with excessive CTEs.
- Writing correct logic but with avoidable alias or column-name errors.
- Finding edge-case bugs during review rather than before submission.

---

# Current Strengths

- Strong understanding of `LAG`, `LEAD`, `ROW_NUMBER`, `RANK`, and cumulative window functions.
- Comfortable with conditional aggregation.
- Understands aggregate-before-window requirements.
- Numeric cast placement is becoming automatic.
- Strong ability to detect hidden edge cases.
- Good understanding of deterministic ordering.
- Able to solve event-log sessionisation problems cleanly.
- Understands correlated subqueries and SQL membership logic.
- Can solve weighted median problems without row expansion.
- Increasing ability to simplify over-engineered SQL.
- Strong instinct for identifying when a solution may fail on unseen data.

---

# Priority Improvements

1. Think directly in SQL rather than writing a mental PySpark solution first.
2. State the grain before writing each major CTE.
3. Run the pre-submit checklist before the first submission.
4. Test one adversarial edge case before submitting.
5. Reduce reflexive use of `DISTINCT`.
6. Use conditional aggregation earlier.
7. Check join fan-out and anchor tables before writing the final aggregation.
8. Add deterministic tie-breakers automatically.
9. Preserve zero-count entities and missing periods.
10. Prefer the simplest query that correctly represents the specification.

---

# Practice Rule

For each new SQL question:

- Identify the final grain.
- Identify the valid output entity or anchor table.
- Decide whether aggregation or deduplication is required before windowing.
- Write the solution directly in SQL.
- Test at least one hidden edge case.
- Run the concise pre-submit checklist.
- Record only genuinely new mistakes or repeated weaknesses.
- Update `sql_focus_areas.md` with detailed learning.
- Update this summary only when the detailed log introduces or materially changes a reusable lesson.

---

# Core Reminder

> Correct SQL is not merely a query that passes the sample. It is a query whose grain, joins, aggregation, ordering, NULL handling, and edge-case behaviour accurately encode the complete specification.