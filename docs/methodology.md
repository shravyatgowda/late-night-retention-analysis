# Methodology

## Question

Does sending lifecycle push notifications in the evening window (21:30 to 22:30) improve day-7 retention and late-night session length compared with sending at random daytime hours?

## Metrics

- **Day-N retention:** share of a signup cohort with at least one session exactly N days after signup (N = 1, 3, 7, 14).
- **Late-night session length:** average minutes per session started between 21:00 and 23:59.
- **Push open rate:** opened pushes / sent pushes.

## Groups

`push_group` is `control` (daytime sends) or `treatment` (21:30 to 22:30 sends), assigned randomly at signup in the simulation.

## Data model

| Table | Key columns |
|---|---|
| `users` | user_id, signup_date, platform, push_group |
| `events` | event_id, user_id, event_name, event_time, session_length_sec |
| `push_sends` | push_id, user_id, sent_at, opened |

## Data quality rules

Before reading any metric, run `sql/05_data_quality_checks.sql`. The synthetic data deliberately contains two problems:

1. About 2% exact duplicate events, removed by the `events_clean` view (`sql/00_clean_view.sql`).
2. About 10% of iOS sessions with a missing length, excluded from session-length averages. In a real product this would be a logging bug to raise with engineering, because it biases iOS session length.

## Limits of this analysis

- The data is synthetic. Effects were planted, so a significant result here proves the code works, not that late-night pushes work.
- In a real study, check sample-ratio mismatch, pre-register the primary metric, and hold out a group that gets no push to separate push effects from organic late-night usage.
- Day-N retention uses "exactly day N". Many teams also track "on or after day N" retention; the two tell different stories.
