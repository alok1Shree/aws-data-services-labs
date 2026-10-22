WITH per_customer AS (
    SELECT customer_id, SUM(amount) AS revenue, COUNT(*) AS orders
    FROM orders_lake.orders
    WHERE status = 'SHIPPED'
    GROUP BY customer_id
)
SELECT customer_id, revenue, orders,
       RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM per_customer
ORDER BY revenue_rank
LIMIT 10;
