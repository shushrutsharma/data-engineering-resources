# SQL Focus Areas — Performance Review Log

> **What this is:** A running record of the recurring weak spots flagged across my DataLemur SQL sessions, newest first. Each item has a concrete before/after example. Use this as the pre-submit checklist and as the "what am I still getting wrong" tracker.
>
> **Repo path:** `data-engineering-interview-preparation/notes/sql_focus_areas.md`
> **Last updated:** 12 Jul 2026 — 🏁 **DataLemur free Hard set COMPLETE** (all free Easy + Medium + Hard done). Sessions 6–8 added: 4 official-solution critiques (repeat-caller → reactivation), senior-managers hierarchy, AWS fleet uptime.

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
| 15 | **Aggregate before window** | "total X" / "total spend" in the prompt = `SUM`/`COUNT` to the stated grain *before* `LAG`/`RANK`. Raw rows ≠ totals; passes 1-row-per-group samples, breaks on real data. |
| 16 | **FLOOR physical counts** | Counts of indivisible units (batches, seats, items) = `FLOOR`, never `ROUND`. Rounding up overflows the physical capacity. |
| 17 | **Join anchor = entity list** | Anchor on the table that *defines valid output rows* (`LEFT JOIN` from it). A payment / lookup / log table is never the anchor — `FULL`/`OUTER` joins leak phantom rows that don't belong in the output. |
| 18 | **Constrain at source, don't filter after** | If I'm pruning overproduction with `DISTINCT` / a join-back / a long CASE ladder, the *generation* step is wrong. Fix it with conditional aggregation, a strict-inequality join, or an anchor join. |
| 19 | **NULLIF the denominator** | Any growth-rate / ratio division needs `NULLIF(denom, 0)`. A zero prior-period makes Postgres raise a *hard* `division by zero` error — it does **not** return NULL. |
| 20 | **Unique tiebreaker on ordered windows** | `LAG` / `LEAD` / `ROW_NUMBER` / `DISTINCT ON` need a deterministic unique sort key. If the business `ORDER BY` can tie (equal timestamps), append the PK (`transaction_id`). `DISTINCT ON` also requires the `ORDER BY` to *lead* with its key. |
| 21 | **Don't filter away zero-counts** | Never `HAVING <computed aggregate> > 0` unless the spec explicitly excludes empty groups. A count of 0 is usually the answer, not noise to strip. |
| 22 | **Gap-fill periods** | Period-over-period queries build the full calendar via `generate_series` + `LEFT JOIN`, not `GROUP BY` over rows that happen to exist. A missing month makes `LAG` compare non-adjacent periods. |

---

## 🗓️ Session 8 — 12 Jul 2026 (evening)
**Milestone:** 🏁 **DataLemur free Hard set COMPLETE** — final Hard (AWS fleet uptime) solved solo and clean, no bugs. **Theme:** *Event-log → sessions via `LEAD`.*

### 8.1 — Interleaved start/stop events → durations *(keeper pattern)*
**Problem:** Sum total server uptime in whole days from a `start`/`stop` event log.
**Pattern (transfers widely):** `LEAD(status_time)` within `partition by server_id order by status_time` pairs each event with the next; filter `WHERE session_status = 'start'` so each start matches its immediately-following stop → every interval counted exactly once, no self-join.

```sql
with sessions as (
    select server_id, status_time as start_time,
        lead(status_time) over (partition by server_id order by status_time) as stop_time,
        session_status
    from server_utilization
)
select floor(sum(extract(epoch from (stop_time - start_time))) / 86400) as total_uptime_days
from sessions
where session_status = 'start';
```
- Dangling final `start` with no stop → `LEAD` = NULL → `SUM` ignores it. Safe by default.
- `FLOOR` for "full days" (checklist #16, now reflexive).
- Same shape as session-duration, time-on-page, machine-uptime: anywhere paired `open`/`close` events sit in adjacent rows, `LEAD` + anchor-row filter beats a self-join.

---

## 🗓️ Session 7 — 12 Jul 2026 (morning)
**Milestone:** Senior-managers hierarchy (manager-of-managers whose own reports aren't senior managers). Couldn't crack it solo — worked a friend's solution to full understanding + built alternatives. **Theme:** *Correlated subqueries & membership joins.* Technique acquisition, not a bug session — these recursion-adjacent hierarchy shapes are a known gap worth a default pattern.

### 7.1 — Correlated subquery mechanics (`NOT EXISTS`)
**Pattern:** The inner subquery re-runs once per outer row, substituting that row's values; `SELECT 1` is a throwaway payload (only existence matters). Read `NOT EXISTS` as a plain-English filter:

```sql
-- "keep this candidate only if NONE of its direct reports is itself a candidate"
select c.manager_id
from candidates c
where not exists (
    select 1 from employees e
    where e.manager_id = c.manager_id                     -- this candidate's reports
      and e.emp_id in (select manager_id from candidates) -- ...is any report also a candidate?
);
```
Rick stays (neither report is a manager-of-managers); John drops (his report Rick *is* one).

### 7.2 — SQL membership constructs → PySpark join types *(the keeper map)*
DataFrame-API equivalents — no manual join keys faking a subquery:

| SQL | PySpark | Use when |
|---|---|---|
| `WHERE x IN (subquery)` | `left_semi` | keep left rows that *have* a match; pull no columns from right |
| `WHERE NOT EXISTS (corr. subquery)` | `left_anti` | keep left rows with *no* match |

Reach for `left_semi` / `left_anti` whenever a subquery only tests membership rather than pulling columns — cheaper and clearer than an inner join + `distinct`.

### 7.3 — `LEFT JOIN` (not INNER) to preserve `COUNT = 0`
**Trap:** In the 2-join version, the grandchild join (`t3`: does this report itself manage someone?) must be `LEFT`. `INNER` drops a candidate whose report manages nobody, so `COUNT(...)` never gets to return 0 for them — they vanish instead of being evaluated. Same NULL-preservation logic as the zero-count work in 6.4.

---

## 🗓️ Session 6 — 11 Jul 2026 (afternoon)
**Milestone:** 4 more DataLemur Hards reviewed — *critiquing the official solutions*, not my own drafts (repeat callers → reactivation count). **Theme:** *Determinism + zero-preservation.* Every bug here passes the dense example table and silently corrupts on the hidden set: either an ordered window with no unique tiebreaker (nondeterministic), or a clause that deletes a legitimate zero/edge row. A quiet failure family, opposite of Session 5's loud overproduction.

### 6.1 — `DISTINCT ON` needs a matching `ORDER BY`
**Problem:** UnitedHealth repeat callers (within 7-day intervals).
**Trap:** `DISTINCT ON (col)` keeps "the first row per group" — but *which* row is first is undefined unless an `ORDER BY` leads with the same `DISTINCT ON` column(s). No `ORDER BY` → Postgres picks an arbitrary row per group, and it can change run to run.

```sql
-- ❌ BUG: which row survives per caller is nondeterministic
select distinct on (caller_id) caller_id, call_time from calls;

-- ✅ FIX: ORDER BY must lead with the DISTINCT ON key, then the real tiebreak
select distinct on (caller_id) caller_id, call_time
from calls
order by caller_id, call_time asc;
```

### 6.2 — Growth-rate landmines: threshold, div-by-zero, gap-fill
**Problem:** Month-over-month growth of long calls (> 5 min). **Three bugs, all invisible on the dense 6-month sample:**

```sql
-- ❌ BUG 1 — threshold: spec says "more than 300s" = strictly greater
where call_duration_secs >= 300      -- wrongly counts exactly-300s calls

-- ❌ BUG 2 — division by zero: a zero-count prior month makes Postgres
--   RAISE a hard `division by zero` error (it does NOT return NULL)
(cnt - lag(cnt) over (order by mth)) * 100.0 / lag(cnt) over (order by mth)

-- ✅ FIX: strict >, and NULLIF the denominator
where call_duration_secs > 300
...
round((cnt - lag(cnt) over (order by mth))::numeric * 100.0
      / nullif(lag(cnt) over (order by mth), 0), 1)
```
**Secondary (gap-fill):** `date_trunc('month', ...)` only emits months that *appear* in the table. A month with zero calls is absent entirely, so `LAG` silently compares e.g. March to January and calls it "month-over-month." Real growth queries need `generate_series` for the full month range + `LEFT JOIN` the counts (missing → 0). NULL is the honest value for "growth from a zero base" (undefined) — same logic as why month 1 is NULL.

### 6.3 — Ordered window with no unique tiebreaker
**Problem:** Duplicate payment detection (`LAG` over `(merchant, card, amount)` by timestamp). Otherwise correct.
**Trap:** `ORDER BY transaction_timestamp` alone. If two rows in a partition share the *exact* timestamp — and a retry-error duplicate charge is a prime candidate — `LAG` pairing is nondeterministic. Same shape as 6.1.

```sql
-- ❌ latent: ties on timestamp → nondeterministic LAG pairing
over (partition by merchant_id, credit_card_id, amount order by transaction_timestamp)

-- ✅ FIX: append the PK as a deterministic tiebreaker
over (partition by merchant_id, credit_card_id, amount
      order by transaction_timestamp asc, transaction_id asc)
```
**Generalized rule (now checklist #20):** any ordering-dependent window whose `ORDER BY` isn't guaranteed unique by the data needs an explicit PK tiebreaker — a default habit, not only when I notice a tie is possible. Hit this twice in one session (`DISTINCT ON` + `LAG`).

### 6.4 — `HAVING <agg> > 0` deletes legitimate zero-count rows
**Problem:** Monthly reactivated-user count.
**Trap:** `HAVING sum(reactivated) > 0` filters my *own aggregation result*. A month where every login is a pure continuation (no reactivations) has a real answer of 0 — the HAVING deletes that row instead of reporting `0`. Passes the sample only because every sampled month happens to have ≥1 reactivation.

```sql
-- ❌ BUG: zero-reactivation months vanish from the output
... group by mnt having sum(case when ... then 1 else 0 end) > 0

-- ✅ FIX: drop the HAVING — a count of 0 IS the answer
... group by mnt order by mnt;
```
Same family as 6.2's div-by-zero: a defensible-looking clause quietly removes a legitimate zero-value data point. Rule: never `HAVING <computed aggregate> > 0` unless the spec explicitly says "exclude empty groups."

---

## 🗓️ Session 5 — 10–11 Jul 2026
**Milestone:** 8 DataLemur Hards attempted (facebook MAU → mckinsey pizza). **Theme:** *Generate-then-filter → constrain-at-source.* The recurring failure across the Hard block: overproduce rows/branches (all permutations, a full outer join, per-entity rows I rejoin, an 8-way CASE), then prune with `DISTINCT` / joins / long CASE ladders. Fix is always to **constrain at generation** — conditional aggregation, strict-inequality joins, anchor joins. This is the same conditional-aggregation reflex from 3.2, now the dominant pattern.

> **Coverage note:** 6 of the 8 Hards are logged here. Two problems from the 10 Jul run aren't recoverable from my chat history — if either surfaced a *distinct* bug, paste it and I'll slot it in as 5.8 / 5.9.

### 5.1 — Aggregate-then-join-back → conditional-aggregation pivot *(the big one)*
**Problem:** Facebook MAU (users active in current AND prior month).
**Trap:** Compute a per-user fact (`count(distinct month)`), throw the rows away, then `JOIN` back to the detail to recover them. Any CTE that aggregates to entity level and then joins back to detail has collapsed information it still needed. 3 CTEs + 1 join where 1 CTE, 0 joins does it.

```sql
-- ❌ OVER-BUILT: filter → group → HAVING count(distinct month) > 1 → join back to detail
-- (3 CTEs + inner join just to re-attach the month)

-- ✅ FIX: pivot the condition INTO a single per-user aggregation. No join.
with flags as (
    select user_id,
        max(case when extract(month from event_date) = 7 then 1 else 0 end) as in_jul,
        max(case when extract(month from event_date) = 6 then 1 else 0 end) as in_jun
    from user_actions
    where extract(year from event_date) = 2022
    group by user_id
)
select 7 as month, count(*) as monthly_active_users
from flags where in_jul = 1 and in_jun = 1;
```
**Diagnostic before writing anything:** (1) final output grain? (2) which entity am I testing a condition on? (3) can the condition be a single aggregate over that entity? If yes → one `GROUP BY`, no join.

### 5.2 — `COUNT(DISTINCT ...) OVER (PARTITION BY ...)` is not portable
**Problem:** Same MAU problem — the PySpark instinct was `approx_count_distinct` over a window.
**Trap:** `COUNT(DISTINCT x) OVER (...)` is unsupported in Postgres (and most engines). Don't reach for a distinct-count window; the conditional-aggregation pivot (5.1) is the portable substitute.

### 5.3 — "total X" is a signal to aggregate to grain *before* windowing
**Problem:** Wayfair year-on-year growth of *total spend* per product.
**Trap:** Applied `LAG(spend)` directly to raw rows. Passes the sample (one txn per product-year) but silently wrong the moment a product has 2+ transactions in a year — `LAG` grabs one row's spend, not the year's sum.

```sql
-- ❌ BUG: LAG over raw rows, no SUM
lag(spend) over (partition by product_id order by extract(year from transaction_date))

-- ✅ FIX: collapse to (product, year) grain FIRST, then window
with yearly as (
    select extract(year from transaction_date) as yr, product_id, sum(spend) as spend
    from user_transactions group by 1, 2
)
select yr, product_id, spend,
    lag(spend) over (partition by product_id order by yr) as prev_spend
from yearly;
```
*Did right here:* `::numeric` cast on the numerator before division (checklist #9 now reflexive), and `LAG` (not `LAG(n,2)`) chosen correctly.

### 5.4 — Counts of indivisible units use FLOOR, never ROUND
**Problem:** Amazon Maximum Prime Item Inventory (fit whole batches into 500,000 sq ft).
**Trap:** `ROUND(leftover_space / batch_size)` for the non-prime batch count. If the leftover fits 6.7 batches, `ROUND` returns 7 → overflows the warehouse. Partial batches don't exist.

```sql
-- ❌ BUG: rounds up, overflows capacity
round((500000 - prime_space * prime_count) / space, 0)

-- ✅ FIX: floor — you can only stock whole batches
floor((500000 - prime_space * prime_count) / space)
```
Secondary trap on this one: leaning on a `LAG(... ) OVER (ORDER BY item_type DESC)` to pull the prime figures across rows is a fragile ordering assumption — safer to compute prime and non-prime as explicit scalars/CTEs than to depend on alphabetical row order.

### 5.5 — Weighted / grouped median from a frequency table *(keeper technique)*
**Problem:** Google median search frequency (buckets of `searches` with `num_users` each; 2T-row expansion is the trap).
**Pattern:** Never expand the rows. Median position(s) = `FLOOR((n+1)/2)` and `CEIL((n+1)/2)` (equal when n odd, adjacent when even). A bucket "owns" position `k` when `prev_cumulative < k <= cumulative`. Average the owning bucket value(s).

```sql
with cte as (
    select searches,
        sum(num_users) over (order by searches) as cum,
        sum(num_users) over (order by searches) - num_users as prev_cum,  -- no 2nd LAG CTE needed
        sum(num_users) over () as total
    from search_frequency
)
select round(avg(searches), 1) as median
from cte
where (prev_cum < floor((total + 1) / 2.0) and cum >= floor((total + 1) / 2.0))
   or (prev_cum < ceil((total + 1) / 2.0)  and cum >= ceil((total + 1) / 2.0));
```
The row-expansion "cheat" (`generate_series(1, num_users)` + `percentile_cont`) is fine to sanity-check the math on a toy input — never for submission, since not-expanding is exactly what's being tested.

### 5.6 — Join anchor = the entity list; collapse symmetric CASE ladders
**Problem:** Facebook advertiser payment status update.
**Trap:** `FULL JOIN advertiser ↔ daily_pay` admits `target`, which exists only in `daily_pay` (a payment log, not an entity list) → a phantom 4th output row. Also an 8-branch CASE that the transition table collapses to 3.

```sql
-- ❌ BUG: FULL JOIN leaks payment-only users into the output; 8-way CASE
-- ✅ FIX: LEFT JOIN anchored on advertiser (the real entity list); 3 branches
select a.user_id,
    case
        when d.paid is not null and a.status = 'CHURN' then 'RESURRECT'
        when d.paid is not null then 'EXISTING'
        else 'CHURN'
    end as new_status
from advertiser a
left join daily_pay d on a.user_id = d.user_id
order by a.user_id;
```
Rule: every "paid" row → EXISTING, except old-status CHURN → RESURRECT; every "not paid" → CHURN. When a transition table has that kind of symmetry, the long CASE is bloat.

### 5.7 — Distinct combinations of k rows: strict-inequality self-join
**Problem:** McKinsey highest-cost 3-topping pizza (no repeated toppings, combinations not permutations).
**Trap:** `CROSS JOIN` twice (n³ permutations) → `!=` to drop same-topping repeats → `DISTINCT` to collapse the 6 permutations per combo. Three mechanisms fighting the same overproduction.

```sql
-- ✅ FIX: chain strict inequalities — one mechanism, does it all
select a.topping_name || ',' || b.topping_name || ',' || c.topping_name as pizza,
       a.ingredient_cost + b.ingredient_cost + c.ingredient_cost as total_cost
from toppings a
join toppings b on a.topping_name < b.topping_name
join toppings c on b.topping_name < c.topping_name
order by total_cost desc, pizza asc;
```
`a < b < c` produces each combination exactly once, already in alphabetical order → no repeats possible, no permutation dupes, no `DISTINCT`. Keep `STRING_AGG(... ORDER BY ...)` in the back pocket only for when column order *isn't* structurally guaranteed (e.g. names from unordered arrays); the `<` join makes it unnecessary here.

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

- **Window-function fluency** — `LAG`, `ROW_NUMBER`, `RANK`, `MAX OVER`, cumulative `SUM OVER` all deployed correctly and by *intent*. Cleared the Google weighted-median problem's core cumulative-sum insight (5.5), which filters out most candidates.
- **`::numeric` cast placement** — now reflexive and correct without prompting (confirmed on Wayfair YoY, 5.3).
- **Typos / name drift** — was the #1 error source (Session 1), now near-zero after dropping the PySpark scaffold.
- **Metacognition** — the "not sure it handles all edge cases" instinct has been a *reliable bug detector* every session. Also demonstrated good judgment knowing when to ask for help (Amazon Prime, 5.4) instead of thrashing. The remaining gap is acting on the checklist *before* submitting, not after being prompted.
- **DataLemur Hard set — CLEARED.** All free Easy + Medium + Hard complete. The final Hard (AWS uptime, 8.1) was a clean solo solve with no bugs — event-log→sessions is now a default shape, not a puzzle.
- **Bug-detection on others' code (new strength).** Session 6 was spotting *latent* correctness bugs in official solutions — nondeterministic windows, div-by-zero, zero-count drops — bugs that never surface on a small sample. This is precisely the review instinct interviews probe with "what breaks on the full dataset?" Strong signal for a Risk/FinCrime DE where silent data corruption is the whole job.

## 🎯 The one thing to fix next
DataLemur is done — more SQL volume is now low-ROI. The single persistent meta-gap across every session is unchanged: **I catch these bugs on review, not on first draft.** Sessions 6–8 prove I can *spot* nondeterminism, div-by-zero, and zero-drops in someone else's code — the transfer is to run the pre-submit checklist against my *own* query before submitting, not after being prompted. That's a 60-second habit, not a skill left to build. Next SQL touch = LeetCode SQL 50 as pure maintenance reps *inside* the Kafka phase.

**Standing note:** SQL is now officially maintenance-level — the DataLemur ladder is fully cleared. The main event starts **tomorrow (13 Jul): Kafka + Spark Structured Streaming** — the block where the risk/streaming-fraud differentiation actually gets built. Do not let SQL polishing (including maintaining this log) become a reason to slip that start date. LeetCode SQL 50 is a daily rep during the streaming block, never a substitute for it.