# Late-Night Retention Analysis

SQL and Python analysis of whether sending push notifications in the 9:30 to 10:30 PM window improves retention and session length for a bedtime-use consumer app.

> **Data disclaimer.** All data in `data/` is simulated (fixed seed, planted effects and planted data-quality bugs). The pipeline is real and runs end to end; the numbers it produces demonstrate the method and are not real product results.

## Questions answered

1. How do D1, D3, D7 and D14 retention differ between push-timing groups?
2. Do late-night sessions run longer for the treatment group?
3. Does push open rate change with send window?
4. Is the data clean enough to trust? (duplicates, missing iOS session lengths)

## Structure

| Path | What it is |
|---|---|
| `data/users.csv`, `events.csv`, `push_sends.csv` | Synthetic input tables |
| `sql/00_clean_view.sql` | De-duplicated events view |
| `sql/01_...` to `sql/04_...` | Retention, session length, push open rate, retention curve |
| `sql/05_data_quality_checks.sql` | Duplicate and missing-value checks by platform |
| `scripts/generate_synthetic_data.py` | Rebuilds the dataset from a fixed seed |
| `scripts/run_analysis.py` | Runs all SQL in SQLite, draws the chart, tests D7 |
| `results/` | Query outputs, `retention_curve.png`, `findings.md` |
| `docs/methodology.md` | Definitions, data model, limitations |

## Run it

```bash
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python scripts/run_analysis.py
```

Open `results/findings.md` for the write-up.

## What this shows

- Production-style SQL: CTEs, joins, conditional aggregation, date arithmetic, de-duplication views.
- Retention and cohort reasoning, including the difference between exact-day and on-or-after retention.
- A data-hygiene step before analysis, with checks that flag duplicate events and an iOS logging gap.
- Honest limits: confounding, lack of a holdout, and why synthetic results are not evidence.

## License

MIT. See `LICENSE`.
