-- Average session length (minutes) for late-night (21:00-23:59) vs other hours, by push group.
-- Sessions with a missing length are excluded and counted separately in the data-quality query.
SELECT u.push_group,
       CASE WHEN CAST(strftime('%H', e.event_time) AS INT) >= 21 THEN 'late_night_21_24' ELSE 'other_hours' END AS hour_window,
       COUNT(*) AS sessions,
       ROUND(AVG(e.session_length_sec) / 60.0, 2) AS avg_session_min
FROM events_clean e
JOIN users u ON u.user_id = e.user_id
WHERE e.session_length_sec IS NOT NULL
GROUP BY u.push_group, hour_window
ORDER BY hour_window, u.push_group;
