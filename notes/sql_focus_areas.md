# SQL Focus Areas — Performance Review Log

> **What this is:** A running record of the recurring weak spots flagged across my DataLemur SQL sessions, newest first. Each item has a concrete before/after example. Use this as the pre-submit checklist and as the "what am I still getting wrong" tracker.
>
> **Repo path:** `data-engineering-interview-preparation/notes/sql_focus_areas.md`
> **Last updated:** 09 Jul 2026 — all 21 and 19 free DataLemur Mediums complete.

---

## ⚡ Master Pre-Submit Checklist

Run this pass on every query *before* hitting submit. Every item traces back to a real bug I shipped — see the dated sections below for the origin.

| # | Check | The one-line rule |
|---|-------|-------------------|
| 1 | **Grain** | What does one row mean at each CTE? Did `date()` / `date_trunc()` / `concat` silently redefine the entity? |
| 2 | **Dedupe before windowing** | If a window's correctness depends on row-position = real sequence (dates, ranks), dedupe first. |
| 3 | **DISTINCT justification** | Only add it if I can *name* the duplicate source. A trailing `DISTINCT` = wrong grain upstream. |
| 4 | **NULL vs empty** | "Empty" in a spec can mean `NULL`, `''`, or whitespace. Cover all three unless data rules one out. |
| 5 | **COUNT vs SUM + else** | `COUNT` → `else` must be NULL. `SUM` → `else 0`. Never `COUNT(...else 0)`. |
| 6 | **RANK vs ROW_NUMBER** | All ties survive → `RANK`. One arbitrary winner → `ROW_NUMBER`. |
| 7 | **Composite ORDER BY** | "rank by A, tie-break B" = one `ROW_NUMBER() OVER (ORDER BY A, B)`. Never chain max+filter. |
| 8 | **Spec-mandated order/format** | If the prompt states an output order or format, treat it as a hard requirement. Test a tie case. |
| 9 | **Cast placement** | `::numeric` goes on the operand *before* division, never on the truncated result. |
| 10 | **Over-build check** | Any CTE that only adds a column to filter on next → fold it into a window `ORDER BY`. |
| 11 | **Reflexive-DISTINCT / dead CTE** | No pass-through CTEs. No window where `GROUP BY` suffices. |
| 12 | **Encode the spec, not the sample** | "At least N" = `HAVING COUNT >= N`. "Has all N" = `HAVING COUNT(DISTINCT x) = N`. Never infer the filter from what the output looks like. |
| 13 | **No parens on column lists** | `GROUP BY a, b` — never `GROUP BY (a, b)` (tuple semantics in Postgres). |
| 14 | **Name drift** | Re-read every CTE/alias name for singular/plural and leftover-from-last-question typos. |

---

## 🗓️ Session 4 — 09 Jul 2026
**Milestone:** All 19 free Mediums complete. **Theme:** Grain discipline is the #1 gap holding SQL below PySpark.

### 4.1 — Grain discipline *(biggest gap)*
**Trap:** Losing track of what one row represents. `LAG` counts *rows*, not *distinct days*; duplicates on the same day break the streak logic.

```sql
-- ❌ BUG: day1, day1, day1, day3 → LAG(2) sees day1 two rows back → false "spree"
lag(t_date, 2) over (partition by user_id order by t_date)   -- on non-deduped rows

-- ✅ FIX: dedupe to one row per (user, day) BEFORE windowing
with df1 as (
    select distinct user_id, date(transaction_date) as t_date
    from transactions
)
```

### 4.2 — Grain via silent truncation
**Trap:** `date()` on a timestamp redefines the grain from "a transaction" to "a day," merging separate events.

```sql
-- ❌ BUG: two separate purchases same day get counted as one "most recent transaction"
count(*) over (partition by user_id, date(transaction_date))

-- ✅ FIX: group on the real transaction grain (full timestamp), then rank
group by user_id, transaction_date
```

### 4.3 — NULL vs empty string
**Trap:** `COALESCE(col, 'n/a')` only rewrites `NULL`. A field "left empty" can be `''` or whitespace — different values than `NULL`.

```sql
-- ❌ BUG: misses '' and '   '
coalesce(call_category, 'n/a') = 'n/a'

-- ✅ FIX: cover NULL, empty, and whitespace
call_category is null or trim(call_category) in ('', 'n/a')
```

### 4.4 — Spec-mandated ORDER BY
**Trap:** Prompt says "sort ascending on ties," query has no `ORDER BY`. Passes the sample (no tie), fails a tie test.

```sql
-- ❌ BUG: undefined output order on ties
select distinct item_count from items_per_order
where order_occurrences = (select max(order_occurrences) from items_per_order);

-- ✅ FIX: RANK keeps all tied modes; explicit ORDER BY satisfies the spec
with ranked as (
    select item_count, rank() over (order by order_occurrences desc) as rnk
    from items_per_order
)
select item_count as mode from ranked where rnk = 1 order by item_count asc;
```

### 4.5 — Simplicity: don't rebuild what's already sortable
**Trap:** `concat` + `to_date` to sort by month, when the integer columns already sort correctly. Engine-fragile for zero benefit.

```sql
-- ❌ OVER-BUILT: string→date reconstruction (breaks on MySQL's unpadded month)
row_number() over (partition by card_name
    order by to_date(concat(issue_month, '-', issue_year), 'MM-YYYY'))

-- ✅ SIMPLER: tuple sort on the raw integers
row_number() over (partition by card_name order by issue_year, issue_month)
```

### 4.6 — Simplicity: rank once, don't cascade filters
**Trap:** Turning each comparison into its own CTE (compute a max → filter → compute count → filter). 4 CTEs *and* a zero-rows bug where 2 CTEs were correct.

```sql
-- ❌ 4 CTEs: max(rating) computed across whole category before the sales filter →
--    a non-competing high-rated row leaks in → tied categories return 0 rows.

-- ✅ FIX: composite ORDER BY does the tiebreak in one ranking pass
row_number() over (
    partition by category_name
    order by total_sales desc, max_rating desc   -- primary, then tiebreak
) as rn
-- ... where rn = 1
```

---

## 🗓️ Session 3 — 07 Jul 2026
**Milestone:** 33 questions (21 Easy + 12 Medium). **Theme:** Edge cases + over-structuring. Root cause = validating against the example dataset, which never contains the adversarial case.

### 3.1 — UNION vs UNION ALL
**Trap:** `UNION` silently collapses legitimate duplicate rows.

```sql
-- ❌ BUG: two real rows with identical values get deduped away
select user_id from a  union  select user_id from b;

-- ✅ FIX: UNION ALL when duplicates are meaningful (and it's cheaper — no dedup sort)
select user_id from a  union all  select user_id from b;
```

### 3.2 — Ties → cartesian product in join approaches
**Trap:** Self-joining on a max/min value multiplies rows when the value ties. Final `DISTINCT` won't save it (rows differ on other columns).

```sql
-- ❌ BUG: 2 tied "highest" months × 1 "lowest" month → 2 rows per ticker

-- ✅ FIX: conditional aggregation collapses to exactly one row per group, no join
select ticker,
    max(case when open = highest_open then month end) as highest_mth,
    max(case when open = lowest_open then month end) as lowest_mth
from df
group by ticker;
```

### 3.3 — Parity / endpoint override
**Trap:** A `max()`-based override that assumes an odd/even endpoint. Correct on the sample, wrong when the dataset ends on the other parity.

```sql
-- ✅ FIX: use LEAD/LAG + COALESCE to handle the boundary row explicitly,
--    rather than a max()-id override that breaks on even/odd endpoints
coalesce(lead(col) over (order by id), col)
```

---

## 🗓️ Session 2 — 06 Jul 2026 (evening)
**Milestone:** DataLemur Q10–20; all 21 free Easy done (last 5–6 pure SQL, no PySpark scaffold). **Theme:** Precision bugs.

### 2.1 — `::numeric` cast placement
**Trap:** Casting *after* integer division — truncation already happened.

```sql
-- ❌ BUG: integer division truncates to 0, then casts 0 to numeric
(count_intl / count_total)::numeric * 100

-- ✅ FIX: cast an operand before dividing
count_intl::numeric / count_total * 100
```

### 2.2 — COALESCE breaking a COUNT(DISTINCT) zero-count
**Trap:** `COALESCE(col, 0)` turns `NULL` into a countable literal, so a genuine zero-count becomes 1.

```sql
-- ❌ BUG: NULLs (meant to count as 0) become a distinct value "0"
count(distinct coalesce(col, 0))

-- ✅ FIX: leave NULLs alone — COUNT already ignores them
count(distinct col)
```

### 2.3 — Secondary sort on the rounded display value
**Trap:** Ordering by the rounded output, not the true aggregate — tie mis-ordering vs expected output.

```sql
-- ❌ BUG: two values round to the same 2dp → order becomes arbitrary
order by round(avg_spend, 2) desc

-- ✅ FIX: sort on the underlying unrounded aggregate
order by avg_spend desc
```

### 2.4 — DISTINCT only with a named duplicate source
**Trap:** Reflexive `DISTINCT` / `dropDuplicates()` as a blanket fix.

```sql
-- ❌ BUG: masks a real fan-out instead of understanding it
select distinct user_id, order_id from ...

-- ✅ RULE: only add DISTINCT when I can name WHY duplicates exist.
--    If it's a one-to-many join fan-out → aggregate with GROUP BY + MAX flag instead.
```

---

## 🗓️ Session 1 — 06 Jul 2026 (morning)
**Milestone:** First 10 DataLemur questions (SQL + PySpark). **Theme:** Mechanical hygiene + reading the spec literally.

### 1.1 — Typos / variable-name drift *(#1 error source: ~7 of 10)*
**Trap:** PySpark-first translation doubles the surface area for names to drift (`df_skill` vs `df_skills`, leftover column names from the previous question).

```sql
-- ❌ BUG: CTE defined as df_skills, referenced as df_skill → NameError-equivalent
with df_skills as (...)
select * from df_skill;   -- typo

-- ✅ FIX: re-read every name before submit. In an interview a broken alias on line 3
--    reads worse than a slightly clumsy query that runs.
```
*(Root cause largely resolved once the PySpark scaffold was dropped mid-Session 2.)*

### 1.2 — Reverse-engineering filters from the sample output
**Trap:** Writing a filter that happens to pass the example instead of encoding the stated requirement.

```sql
-- ❌ BUG: "candidate has ALL 3 skills" written as membership → passes sample, wrong on edge
where skill in ('Python', 'Tableau', 'PostgreSQL')

-- ✅ FIX: encode the literal requirement
group by candidate_id
having count(distinct skill) = 3
```

### 1.3 — Parentheses around column lists
**Trap:** Wrapping `GROUP BY` / `ORDER BY` / `PARTITION BY` column lists in parens triggers tuple/row-value semantics in Postgres — a different, rarer feature.

```sql
-- ❌ BUG: tuple semantics, not a column-list grouping
group by (user_id, category)

-- ✅ FIX
group by user_id, category
```

### 1.4 — Over-reaching for structure
**Trap:** Dead pass-through CTEs, and reaching for a window function where a plain `GROUP BY` suffices.

```sql
-- ❌ OVER-BUILT: window to get a per-group total, then aggregate anyway
sum(x) over (partition by g)   -- when the query only needs one row per group

-- ✅ SIMPLER: just aggregate
select g, sum(x) from t group by g
```

---

## 📈 Trajectory (what's improving)

- **Window-function fluency** — `LAG`, `ROW_NUMBER`, `RANK`, `MAX OVER` all deployed correctly and by *intent*, not habit.
- **Typos / name drift** — was the #1 error source (Session 1), now near-zero after dropping the PySpark scaffold.
- **Metacognition** — the "not sure it handles all edge cases" instinct has been a *reliable bug detector* every session. The remaining gap is acting on it (running this checklist) *before* submitting, not after being prompted.

**Standing note:** SQL is now maintenance-level, not the main event. Keep it to a daily rep and protect the Kafka + Spark Streaming window (starts 13 Jul) — that block is where the risk/streaming-fraud differentiation actually gets built.
