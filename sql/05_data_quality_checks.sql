-- Daily validation checks. Run before trusting any metric.
-- 1) Exact duplicate events, by platform.
-- 2) Share of sessions with a missing length, by platform.
SELECT u.platform,
       COUNT(*) AS raw_events,
       COUNT(*) - COUNT(DISTINCT e.user_id || '|' || e.event_name || '|' || e.event_time) AS duplicate_rows,
       ROUND(100.0 * (COUNT(*) - COUNT(DISTINCT e.user_id || '|' || e.event_name || '|' || e.event_time)) / COUNT(*), 2) AS duplicate_pct,
       ROUND(100.0 * SUM(CASE WHEN e.session_length_sec IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS missing_length_pct
FROM events e
JOIN users u ON u.user_id = e.user_id
GROUP BY u.platform
ORDER BY u.platform;
