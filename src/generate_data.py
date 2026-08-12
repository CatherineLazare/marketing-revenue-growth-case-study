"""Generate a deterministic, realistic synthetic B2B SaaS lead dataset."""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "leads.csv"
random.seed(20260812)

channels = {
    "Paid Social": {"share": 0.30, "mql": 0.40, "sql": 0.28, "opp": 0.55, "win": 0.24, "response": 41},
    "Paid Search": {"share": 0.22, "mql": 0.56, "sql": 0.43, "opp": 0.60, "win": 0.28, "response": 20},
    "Organic Search": {"share": 0.18, "mql": 0.53, "sql": 0.47, "opp": 0.61, "win": 0.30, "response": 18},
    "Webinar": {"share": 0.12, "mql": 0.64, "sql": 0.34, "opp": 0.58, "win": 0.27, "response": 28},
    "Partner": {"share": 0.10, "mql": 0.67, "sql": 0.54, "opp": 0.66, "win": 0.33, "response": 16},
    "Email Nurture": {"share": 0.08, "mql": 0.48, "sql": 0.39, "opp": 0.57, "win": 0.26, "response": 25},
}
campaigns = {
    "Paid Social": ["LinkedIn Scale", "ABM Retargeting"], "Paid Search": ["High Intent Search", "Competitor Search"],
    "Organic Search": ["SEO Content Hub", "Product Comparison"], "Webinar": ["CFO Roundtable", "Revenue Operations Live"],
    "Partner": ["Agency Referral", "Technology Alliance"], "Email Nurture": ["Lifecycle Nurture", "Reactivation Series"],
}
segments = [("SMB", 0.42, 12000), ("Mid-Market", 0.40, 28000), ("Enterprise", 0.18, 65000)]

def choose_weighted(items):
    total = sum(item[1] for item in items)
    n = random.random() * total
    for item in items:
        n -= item[1]
        if n <= 0:
            return item
    return items[-1]

def pick_channel():
    return choose_weighted([(name, details["share"]) for name, details in channels.items()])[0]

def main():
    OUT.parent.mkdir(exist_ok=True)
    fields = ["lead_id", "created_date", "channel", "campaign", "company_segment", "industry", "employee_count", "lead_score", "first_response_hours", "mql_date", "sql_date", "opportunity_date", "customer_date", "expected_arr", "status"]
    industries = ["SaaS", "Financial Services", "Healthcare", "Professional Services", "Manufacturing", "Retail"]
    start = date(2025, 1, 1)
    rows = []
    for i in range(1, 12001):
        channel = pick_channel(); profile = channels[channel]
        segment, _, arr_base = choose_weighted(segments)
        created = start + timedelta(days=random.randrange(548))
        response = max(1, round(random.gauss(profile["response"], profile["response"] * 0.45), 1))
        # Response delays above 24 hours reduce sales acceptance, modelling an operational leak.
        sql_rate = profile["sql"] * (0.72 if response > 24 else 1)
        mql = random.random() < profile["mql"]
        sql = mql and random.random() < sql_rate
        opp = sql and random.random() < profile["opp"]
        customer = opp and random.random() < profile["win"]
        mql_date = created + timedelta(days=random.randint(1, 10)) if mql else None
        sql_date = mql_date + timedelta(days=random.randint(1, 16)) if sql else None
        opp_date = sql_date + timedelta(days=random.randint(4, 30)) if opp else None
        customer_date = opp_date + timedelta(days=random.randint(10, 55)) if customer else None
        expected_arr = round(arr_base * random.uniform(0.72, 1.32), -2) if opp else 0
        status = "Customer" if customer else "Opportunity" if opp else "SQL" if sql else "MQL" if mql else "Lead"
        rows.append([f"L{i:05d}", created.isoformat(), channel, random.choice(campaigns[channel]), segment, random.choice(industries), random.choice([25, 75, 150, 350, 750, 1500, 5000]), random.randint(20, 98), response, *(d.isoformat() if d else "" for d in [mql_date, sql_date, opp_date, customer_date]), int(expected_arr), status])
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f); writer.writerow(fields); writer.writerows(rows)
    print(f"Wrote {len(rows):,} synthetic leads to {OUT}")

if __name__ == "__main__": main()
