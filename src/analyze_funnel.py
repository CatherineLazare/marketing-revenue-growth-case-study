"""Create reproducible funnel tables and revenue-leak estimates from leads.csv."""
from __future__ import annotations
import csv, json, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, OUTPUTS, DB = ROOT / "data" / "leads.csv", ROOT / "outputs", ROOT / "revenue_case_study.db"
OUTPUTS.mkdir(exist_ok=True)

def pct(n, d): return round(100 * n / d, 1) if d else 0
def main():
    rows = list(csv.DictReader(DATA.open(encoding="utf-8")))
    for r in rows:
        for key in ("first_response_hours", "expected_arr"): r[key] = float(r[key])
    groups = {}
    for r in rows: groups.setdefault(r["channel"], []).append(r)
    table = []
    for channel, g in groups.items():
        lead, mql, sql, opp, cust = len(g), sum(bool(x["mql_date"]) for x in g), sum(bool(x["sql_date"]) for x in g), sum(bool(x["opportunity_date"]) for x in g), sum(bool(x["customer_date"]) for x in g)
        arr = sum(x["expected_arr"] for x in g)
        table.append({"channel": channel, "leads": lead, "mqls": mql, "sqls": sql, "opportunities": opp, "customers": cust, "mql_rate": pct(mql, lead), "mql_sql_rate": pct(sql, mql), "win_rate": pct(cust, opp), "expected_arr": round(arr), "avg_response_hours": round(sum(x["first_response_hours"] for x in g)/lead, 1)})
    table.sort(key=lambda x: x["expected_arr"], reverse=True)
    with (OUTPUTS / "channel_funnel.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=table[0].keys()); w.writeheader(); w.writerows(table)
    overall_mql_sql = sum(x["sqls"] for x in table) / sum(x["mqls"] for x in table)
    leak = []
    for x in table:
        shortfall = max(0, overall_mql_sql - x["mql_sql_rate"]/100)
        avg_arr = x["expected_arr"] / x["opportunities"] if x["opportunities"] else 0
        # Conversion recovery valued at average opportunity ARR and current opportunity-to-customer rate.
        value = round(x["mqls"] * shortfall * avg_arr * (x["win_rate"]/100))
        if value: leak.append({"channel": x["channel"], "annualized_revenue_at_risk": value})
    late = [r for r in rows if r["mql_date"] and r["first_response_hours"] > 24]
    fast = [r for r in rows if r["mql_date"] and r["first_response_hours"] <= 24]
    def sqlrate(g): return sum(bool(r["sql_date"]) for r in g)/len(g) if g else 0
    late_value = round(sum(r["expected_arr"] for r in late if r["opportunity_date"]) * max(0, sqlrate(fast)-sqlrate(late)) * 1.7)
    summary = {"total_leads": len(rows), "total_mqls": sum(bool(r["mql_date"]) for r in rows), "total_sqls": sum(bool(r["sql_date"]) for r in rows), "total_expected_arr": round(sum(r["expected_arr"] for r in rows)), "overall_mql_sql_rate": round(overall_mql_sql*100, 1), "late_response_revenue_at_risk": late_value, "channel_revenue_leak": leak}
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with sqlite3.connect(DB) as conn:
        conn.execute("DROP TABLE IF EXISTS leads")
        cols = list(rows[0]); conn.execute("CREATE TABLE leads (" + ",".join(f'[{c}] TEXT' for c in cols) + ")")
        conn.executemany("INSERT INTO leads VALUES (" + ",".join("?"*len(cols)) + ")", [[r[c] for c in cols] for r in rows])
    print(json.dumps(summary, indent=2))
if __name__ == "__main__": main()
