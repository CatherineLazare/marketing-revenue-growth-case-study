# Revenue Leak Analysis | Growth Marketing Case Study

An end-to-end marketing analytics project that investigates where leads are leaking from a B2B SaaS funnel and translates the analysis into a clear revenue plan.

## Executive summary

Analysis of **12,000 simulated leads** shows that the largest preventable leak occurs between marketing-qualified leads (MQLs) and sales-qualified leads (SQLs). Paid social is producing volume, but its MQL-to-SQL conversion rate trails the portfolio, while slow sales follow-up compounds the loss.

| Opportunity | Estimated annualized revenue at risk | Recommended action |
|---|---:|---|
| Paid-social lead qualification gap | $637,560 | Tighten audience and introduce a qualification nurture path |
| Slow follow-up on high-intent leads | $575,226 | Set a <24-hour sales-response SLA and alert on breaches |
| Low webinar MQL-to-SQL conversion | $306,507 | Add intent scoring and sales-assisted webinar follow-up |
| **Total prioritized opportunity** | **$1,519,293** | Run a 90-day funnel recovery plan |

These estimates are directional, based on expected deal value, observed stage conversion, and lead cohorts in the included synthetic dataset. See the assumptions in [`reports/revenue_leak_analysis.md`](reports/revenue_leak_analysis.md).

## What’s included

- [`data/leads.csv`](data/leads.csv) — 12,000 reproducibly simulated B2B SaaS leads
- [`src/generate_data.py`](src/generate_data.py) — deterministic dataset generator
- [`src/analyze_funnel.py`](src/analyze_funnel.py) — Python analysis that writes the KPI tables
- [`sql/funnel_analysis.sql`](sql/funnel_analysis.sql) — portable SQLite SQL for funnel and revenue-leak analysis
- [`dashboard/index.html`](dashboard/index.html) — self-contained interactive, Power BI-style dashboard
- [`reports/revenue_leak_analysis.md`](reports/revenue_leak_analysis.md) — methodology, findings, and quantified leakage
- [`reports/executive_recommendation.md`](reports/executive_recommendation.md) — 90-day recommendation for a marketing manager

## Business question

How can a growth-marketing team reduce conversion leakage, improve the quality of handoffs to sales, and recover the highest-value revenue opportunity?

## Funnel definition

`Lead → MQL → SQL → Opportunity → Customer`

The primary diagnostic is MQL-to-SQL conversion: it is the point where marketing intent becomes a sales-accepted conversation. The project also measures follow-up speed, expected revenue, and performance by channel and campaign.

## Reproduce the analysis

Requires Python 3.10+; the standard library is sufficient.

```bash
python src/generate_data.py
python src/analyze_funnel.py
```

The second command refreshes `outputs/channel_funnel.csv`, `outputs/campaign_funnel.csv`, and `outputs/summary.json`. Open `dashboard/index.html` in a browser to explore the dashboard.

To run the SQL directly:

```bash
sqlite3 revenue_case_study.db < sql/funnel_analysis.sql
```

Load `data/leads.csv` into a table named `leads` first. The Python analysis creates this SQLite database automatically.

## Dashboard preview

The dashboard highlights funnel health, channel comparison, response-time performance, and the prioritized revenue-leak opportunities. It uses the generated output CSVs and Plotly from a CDN, so it can be opened locally without a server.

## Data note

All records are synthetic. Names, companies, and outcomes are simulated solely for this portfolio case study; no customer or prospect data is included.
