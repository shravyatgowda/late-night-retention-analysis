"""Run all SQL in sql/ on the synthetic CSVs (SQLite), save outputs, draw the retention chart,
and test the D7 difference. Writes results/*.csv, results/retention_curve.png, results/findings.md
"""
import glob
import sqlite3
from statistics import NormalDist

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

conn = sqlite3.connect(":memory:")
for t in ["users", "events", "push_sends"]:
    pd.read_csv(f"data/{t}.csv").to_sql(t, conn, index=False)

out = {}
for path in sorted(glob.glob("sql/*.sql")):
    name = path.split("/")[-1][:-4]
    sql = open(path).read()
    if name.startswith("00_"):
        conn.executescript(sql)
        continue
    df = pd.read_sql_query(sql, conn)
    df.to_csv(f"results/{name}.csv", index=False)
    out[name] = df

# Chart
curve = out["04_retention_curve"]
fig, ax = plt.subplots(figsize=(7, 4))
for grp, g in curve.groupby("push_group"):
    ax.plot(g.day_n, g.retention_pct, marker="o", label=grp)
ax.set_xlabel("Days since signup")
ax.set_ylabel("Users active (%)")
ax.set_title("Retention curve by push timing (synthetic data)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("results/retention_curve.png", dpi=150)

# D7 significance (two-proportion z-test)
users = pd.read_sql_query("SELECT push_group, COUNT(*) n FROM users GROUP BY push_group", conn).set_index("push_group").n
ret = out["01_retention_d1_d3_d7_d14"].set_index("push_group")
p1, p2 = ret.loc["control", "d7_pct"] / 100, ret.loc["treatment", "d7_pct"] / 100
n1, n2 = users["control"], users["treatment"]
pool = (p1 * n1 + p2 * n2) / (n1 + n2)
z = (p2 - p1) / (pool * (1 - pool) * (1 / n1 + 1 / n2)) ** 0.5
pval = 2 * (1 - NormalDist().cdf(abs(z)))
se = (p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** 0.5
lo, hi = (p2 - p1) - 1.96 * se, (p2 - p1) + 1.96 * se


def md(df):
    return df.to_markdown(index=False) if hasattr(df, "to_markdown") else df.to_string(index=False)


try:
    import tabulate  # noqa: F401
except ImportError:
    md = lambda df: "```\n" + df.to_string(index=False) + "\n```"  # noqa: E731

lines = [
    "# Findings (SYNTHETIC DATA)", "",
    "> The data is simulated with planted effects. These numbers show how the analysis works, not real product results.", "",
    "## Retention by push group", "", md(out["01_retention_d1_d3_d7_d14"]), "",
    f"D7 difference: {(p2 - p1) * 100:+.1f} points (95% CI {lo * 100:+.1f} to {hi * 100:+.1f}), z = {z:.2f}, p = {pval:.4f}.", "",
    "![retention curve](retention_curve.png)", "",
    "## Session length, late night vs other hours", "", md(out["02_session_length_by_hour_window"]), "",
    "## Push open rate by send window", "", md(out["03_push_open_rate_by_send_window"]), "",
    "## Data quality", "", md(out["05_data_quality_checks"]), "",
    "Caveat: the treatment group differs from control in push timing only by design, but push timing is confounded with push volume in this toy setup, and no holdout for organic late-night usage exists. A real study would randomize and pre-register these.", "",
]
open("results/findings.md", "w").write("\n".join(lines))
print("\n".join(lines))
