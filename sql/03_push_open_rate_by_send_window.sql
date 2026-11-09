-- Push open rate by group and send-hour window.
SELECT u.push_group,
       CASE WHEN CAST(strftime('%H', p.sent_at) AS INT) BETWEEN 21 AND 22 THEN 'evening_21_23'
            ELSE 'daytime' END AS send_window,
       COUNT(*) AS pushes,
       ROUND(100.0 * AVG(p.opened), 1) AS open_rate_pct
FROM push_sends p
JOIN users u ON u.user_id = p.user_id
GROUP BY u.push_group, send_window
ORDER BY u.push_group;
