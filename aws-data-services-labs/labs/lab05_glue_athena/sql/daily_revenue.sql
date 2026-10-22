-- Partition pruning: filtering on dt means Athena only scans those folders (cost + speed).
SELECT dt,
       COUNT(*)                                   AS orders,
       ROUND(SUM(amount), 2)                      AS revenue,
       ROUND(AVG(amount), 2)                      AS avg_order_value
FROM orders_lake.orders
WHERE dt BETWEEN '2026-01-01' AND '2026-01-03'
  AND status <> 'CANCELLED'
GROUP BY dt
ORDER BY dt;
