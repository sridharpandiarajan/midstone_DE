-- Midstone 4: Kavitha's six questions.

-- Q1. Orders and revenue per city.
SELECT r.city,
       COUNT(*) AS orders,
       ROUND(SUM(CASE WHEN o.status = 'delivered' THEN o.total_amount ELSE 0 END), 2) AS revenue
FROM orders o
JOIN restaurants r ON r.restaurant_id = o.restaurant_id
GROUP BY r.city
ORDER BY revenue DESC;

-- Q2. Top 5 restaurants per city by revenue.
SELECT city, revenue_rank, restaurant_id, restaurant_name, revenue
FROM (
    SELECT r.city,
           r.restaurant_id,
           r.name AS restaurant_name,
           ROUND(SUM(o.total_amount), 2) AS revenue,
           RANK() OVER (PARTITION BY r.city ORDER BY SUM(o.total_amount) DESC) AS revenue_rank
    FROM orders o
    JOIN restaurants r ON r.restaurant_id = o.restaurant_id
    WHERE o.status = 'delivered'
    GROUP BY r.city, r.restaurant_id, r.name
) ranked
WHERE revenue_rank <= 5
ORDER BY city, revenue_rank;

-- Q3. Average delivery minutes per restaurant.
SELECT restaurant_id,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE, order_ts, delivered_ts)), 2) AS avg_delivery_minutes
FROM orders
WHERE status = 'delivered'
GROUP BY restaurant_id
ORDER BY restaurant_id;

-- Q4. Customers who ordered more than once.
SELECT customer_id, COUNT(*) AS orders
FROM orders
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY orders DESC, customer_id;

-- Q5. Failed payments per city.
SELECT r.city, COUNT(*) AS failed_payments
FROM payments p
JOIN orders o ON o.order_id = p.order_id
JOIN restaurants r ON r.restaurant_id = o.restaurant_id
WHERE p.status = 'failed'
GROUP BY r.city
ORDER BY failed_payments DESC;

-- Q6. Revenue per hour, with a running total over the day.
SELECT order_hour,
       revenue,
       ROUND(SUM(revenue) OVER (ORDER BY order_hour), 2) AS running_revenue
FROM (
    SELECT HOUR(order_ts) AS order_hour,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE status = 'delivered'
    GROUP BY HOUR(order_ts)
) hourly
ORDER BY order_hour;
