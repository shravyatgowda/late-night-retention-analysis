-- Classic day-N retention by push group: share of users with a session exactly N days after signup.
WITH active_days AS (
  SELECT DISTINCT user_id, date(event_time) AS d FROM events_clean
)
SELECT u.push_group,
       COUNT(DISTINCT u.user_id) AS users,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN CAST(julianday(a.d) - julianday(u.signup_date) AS INT) = 1  THEN u.user_id END) / COUNT(DISTINCT u.user_id), 1) AS d1_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN CAST(julianday(a.d) - julianday(u.signup_date) AS INT) = 3  THEN u.user_id END) / COUNT(DISTINCT u.user_id), 1) AS d3_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN CAST(julianday(a.d) - julianday(u.signup_date) AS INT) = 7  THEN u.user_id END) / COUNT(DISTINCT u.user_id), 1) AS d7_pct,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN CAST(julianday(a.d) - julianday(u.signup_date) AS INT) = 14 THEN u.user_id END) / COUNT(DISTINCT u.user_id), 1) AS d14_pct
FROM users u
LEFT JOIN active_days a ON a.user_id = u.user_id
GROUP BY u.push_group
ORDER BY u.push_group;
