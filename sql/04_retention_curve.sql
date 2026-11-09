-- Retention curve for day 0..14 by push group (used for the chart).
WITH active_days AS (
  SELECT DISTINCT user_id, date(event_time) AS d FROM events_clean
),
group_sizes AS (
  SELECT push_group, COUNT(*) AS n FROM users GROUP BY push_group
),
day_counts AS (
  SELECT u.push_group,
         CAST(julianday(a.d) - julianday(u.signup_date) AS INT) AS day_n,
         COUNT(DISTINCT u.user_id) AS active_users
  FROM users u
  JOIN active_days a ON a.user_id = u.user_id
  GROUP BY u.push_group, day_n
)
SELECT c.push_group, c.day_n, ROUND(100.0 * c.active_users / g.n, 2) AS retention_pct
FROM day_counts c
JOIN group_sizes g ON g.push_group = c.push_group
WHERE c.day_n BETWEEN 0 AND 14
ORDER BY c.push_group, c.day_n;
