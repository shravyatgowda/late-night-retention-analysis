"""Generate SYNTHETIC app data for the late-night retention analysis.

Tables: users, events (session_start), push_sends.
The treatment group gets push notifications between 21:30 and 22:30 local time; control gets
them at random daytime hours. The effect on retention and session length is planted so the
SQL has something to find. Data-quality problems (duplicates, missing iOS session lengths)
are planted on purpose so the validation queries have something to catch.
Nothing here is real user data.
"""
import numpy as np
import pandas as pd

SEED = 7
N_USERS = 3000
rng = np.random.default_rng(SEED)

signup = pd.Timestamp("2026-09-01") + pd.to_timedelta(rng.integers(0, 21, N_USERS), unit="D")
users = pd.DataFrame({
    "user_id": [f"u{200000 + i}" for i in range(N_USERS)],
    "signup_date": signup.strftime("%Y-%m-%d"),
    "platform": rng.choice(["android", "ios"], N_USERS, p=[0.78, 0.22]),
    "push_group": rng.choice(["control", "treatment"], N_USERS),
})

# P(active on day d | signup) for control; treatment gets a growing relative lift.
base = [1.0, 0.42, 0.33, 0.28, 0.25, 0.23, 0.21, 0.19, 0.18, 0.17, 0.16, 0.155, 0.15, 0.145, 0.14]
lift = [1.0, 1.06, 1.10, 1.14, 1.18, 1.22, 1.26, 1.30, 1.30, 1.30, 1.30, 1.30, 1.30, 1.30, 1.30]

HOUR_W = np.array([1, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 7, 8, 8, 7, 5, 3], dtype=float)
HOUR_W /= HOUR_W.sum()

rows = []
for u in users.itertuples():
    treat = u.push_group == "treatment"
    for d in range(15):
        p = min(base[d] * (lift[d] if treat else 1.0), 1.0)
        if rng.random() < p:
            for _ in range(rng.integers(1, 4)):
                if treat and rng.random() < 0.55:
                    hour = int(rng.choice([21, 22, 23], p=[0.35, 0.4, 0.25]))
                else:
                    hour = int(rng.choice(24, p=HOUR_W))
                minute, second = int(rng.integers(0, 60)), int(rng.integers(0, 60))
                ts = pd.Timestamp(u.signup_date) + pd.Timedelta(days=d, hours=hour, minutes=minute, seconds=second)
                length = rng.lognormal(mean=5.9, sigma=0.7)  # median ~6 min
                if treat and 21 <= hour <= 23:
                    length *= 1.22
                rows.append((u.user_id, "session_start", ts, round(length), u.platform))

events = pd.DataFrame(rows, columns=["user_id", "event_name", "event_time", "session_length_sec", "platform"])

# Planted data-quality issues
events.loc[(events.platform == "ios") & (rng.random(len(events)) < 0.10), "session_length_sec"] = np.nan
dups = events.sample(frac=0.02, random_state=SEED)
events = pd.concat([events, dups]).sort_values(["event_time", "user_id"]).reset_index(drop=True)
events.insert(0, "event_id", [f"e{i}" for i in range(len(events))])
events["event_time"] = events["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
events = events.drop(columns=["platform"])

# Push sends: one per user per day for first 7 days
push = []
for u in users.itertuples():
    treat = u.push_group == "treatment"
    for d in range(1, 8):
        if treat:
            hh, mm = 21, 30 + int(rng.integers(0, 60))
            if mm >= 60:
                hh, mm = 22, mm - 60
        else:
            hh, mm = int(rng.integers(10, 20)), int(rng.integers(0, 60))
        ts = pd.Timestamp(u.signup_date) + pd.Timedelta(days=d, hours=hh, minutes=mm)
        opened = rng.random() < (0.24 if treat else 0.15)
        push.append((ts.strftime("%Y-%m-%d %H:%M:%S"), u.user_id, int(opened)))
push = pd.DataFrame(push, columns=["sent_at", "user_id", "opened"])
push.insert(0, "push_id", [f"p{i}" for i in range(len(push))])

users.to_csv("data/users.csv", index=False)
events.to_csv("data/events.csv", index=False)
push.to_csv("data/push_sends.csv", index=False)
print(len(users), "users;", len(events), "events;", len(push), "push sends")
