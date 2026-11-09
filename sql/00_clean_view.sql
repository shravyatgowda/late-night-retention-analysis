-- De-duplicated events. Rows identical on (user_id, event_name, event_time) are collapsed to one.
CREATE VIEW events_clean AS
SELECT MIN(event_id) AS event_id, user_id, event_name, event_time, MAX(session_length_sec) AS session_length_sec
FROM events
GROUP BY user_id, event_name, event_time;
