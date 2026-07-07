with df_even as (
    select item as item_e,
    order_id - 1 as order_id_e
    from orders
    where order_id % 2 = 0

),

df_odd as (
    select item as item_o,
    order_id + 1 as order_id_o
    from orders
    where order_id % 2 != 0
),
    
df_join1 as (
    select b.order_id, b.item, e.item_e
    from orders b
    left join df_even e
    on b.order_id = e.order_id_e
),

df_join2 as (
    select j.order_id, j.item, j.item_e, o.item_o
    from df_join1 j
    left join df_odd o
    on j.order_id = o.order_id_o
),

df_final as (

    select order_id,
    case
        when order_id = (select max(order_id) from orders) and order_id % 2 != 0 then item
        when order_id != (select max (order_id) from orders) and item_e is NULL then item_o
        when order_id != (select max (order_id) from orders) and item_o is NULL then item_e
        else item
    end as item_final
    from df_join2

)

select order_id, item_final as item
from df_final
order by order_id asc


## smarter way:

with df as (
    select order_id, item,
        lead(item) over (order by order_id) as next_item,
        lag(item) over (order by order_id) as prev_item
    from orders
)

select order_id,
    case
        when order_id % 2 != 0 then coalesce(next_item, item)
        else prev_item
    end as item
from df
order by order_id asc