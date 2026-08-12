"""
Marketing Revenue & Growth Case Study

Purpose:
Analyze a simulated B2B marketing funnel to identify:
1. Funnel conversion bottlenecks
2. Marketing channel performance
3. Revenue and pipeline contribution
4. Potential revenue leakage
5. Growth opportunities

Author: Catherine Lazare
"""

import pandas as pd


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_FILE = "../data/simulated_b2b_marketing_funnel.csv"

df = pd.read_csv(DATA_FILE)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def conversion_rate(numerator, denominator):
    """Return conversion rate as a percentage."""
    if denominator == 0:
        return 0

    return round((numerator / denominator) * 100, 2)


def money(value):
    """Format numeric values as dollars."""
    return f"${value:,.0f}"


# ============================================================
# 3. OVERALL FUNNEL ANALYSIS
# ============================================================

leads = len(df)

mqls = df["mql"].sum()
sqls = df["sql"].sum()
opportunities = df["opportunity"].sum()
customers = df["customer"].sum()

pipeline_value = df["pipeline_value"].sum()
revenue = df["revenue"].sum()
marketing_spend = df["marketing_spend"].sum()


lead_to_mql = conversion_rate(mqls, leads)
mql_to_sql = conversion_rate(sqls, mqls)
sql_to_opportunity = conversion_rate(opportunities, sqls)
opportunity_to_customer = conversion_rate(customers, opportunities)
overall_conversion = conversion_rate(customers, leads)


print("\n" + "=" * 70)
print("MARKETING REVENUE & GROWTH ANALYSIS")
print("=" * 70)


print("\nOVERALL FUNNEL")
print("-" * 70)

print(f"Leads:                 {leads:,}")
print(f"MQLs:                  {mqls:,} ({lead_to_mql}%)")
print(f"SQLs:                  {sqls:,} ({mql_to_sql}% of MQLs)")
print(
    f"Opportunities:         {opportunities:,} "
    f"({sql_to_opportunity}% of SQLs)"
)
print(
    f"Customers:             {customers:,} "
    f"({opportunity_to_customer}% of opportunities)"
)
print(f"Overall Lead-to-Customer: {overall_conversion}%")


print("\nFINANCIAL PERFORMANCE")
print("-" * 70)

print(f"Marketing Spend:       {money(marketing_spend)}")
print(f"Pipeline Value:        {money(pipeline_value)}")
print(f"Revenue:               {money(revenue)}")

if marketing_spend > 0:
    revenue_to_spend = revenue / marketing_spend
else:
    revenue_to_spend = 0

print(f"Revenue / Marketing Spend: {revenue_to_spend:.2f}x")


# ============================================================
# 4. IDENTIFY FUNNEL BOTTLENECKS
# ============================================================

funnel_rates = {
    "Lead → MQL": lead_to_mql,
    "MQL → SQL": mql_to_sql,
    "SQL → Opportunity": sql_to_opportunity,
    "Opportunity → Customer": opportunity_to_customer
}

bottleneck = min(funnel_rates, key=funnel_rates.get)


print("\nFUNNEL BOTTLENECK")
print("-" * 70)

print(
    f"The weakest conversion stage is: {bottleneck} "
    f"({funnel_rates[bottleneck]}%)"
)


# ============================================================
# 5. MARKETING CHANNEL ANALYSIS
# ============================================================

channel_summary = (
    df.groupby("channel")
    .agg(
        leads=("lead_id", "count"),
        mqls=("mql", "sum"),
        sqls=("sql", "sum"),
        opportunities=("opportunity", "sum"),
        customers=("customer", "sum"),
        revenue=("revenue", "sum"),
        marketing_spend=("marketing_spend", "sum")
    )
    .reset_index()
)


channel_summary["lead_to_mql_pct"] = (
    channel_summary["mqls"]
    / channel_summary["leads"]
    * 100
)


channel_summary["mql_to_sql_pct"] = (
    channel_summary["sqls"]
    / channel_summary["mqls"]
    * 100
)


channel_summary["sql_to_opportunity_pct"] = (
    channel_summary["opportunities"]
    / channel_summary["sqls"]
    * 100
)


channel_summary["opportunity_to_customer_pct"] = (
    channel_summary["customers"]
    / channel_summary["opportunities"]
    * 100
)


channel_summary["revenue_to_spend"] = (
    channel_summary["revenue"]
    / channel_summary["marketing_spend"]
)


print("\nCHANNEL PERFORMANCE")
print("-" * 70)

display_columns = [
    "channel",
    "leads",
    "mqls",
    "sqls",
    "opportunities",
    "customers",
    "revenue",
    "revenue_to_spend"
]

print(
    channel_summary
    .sort_values("revenue", ascending=False)
    [display_columns]
    .to_string(index=False)
)


# ============================================================
# 6. IDENTIFY TOP CHANNEL
# ============================================================

top_revenue_channel = (
    channel_summary
    .sort_values("revenue", ascending=False)
    .iloc[0]
)


top_efficiency_channel = (
    channel_summary
    .sort_values("revenue_to_spend", ascending=False)
    .iloc[0]
)


print("\nCHANNEL INSIGHTS")
print("-" * 70)

print(
    f"Highest revenue channel: "
    f"{top_revenue_channel['channel']} "
    f"({money(top_revenue_channel['revenue'])})"
)

print(
    f"Most efficient channel: "
    f"{top_efficiency_channel['channel']} "
    f"({top_efficiency_channel['revenue_to_spend']:.2f}x revenue/spend)"
)


# ============================================================
# 7. REVENUE LEAKAGE ANALYSIS
# ============================================================

"""
Revenue leakage methodology:

Instead of claiming that every prospect who drops out
would have become a customer, we estimate an opportunity
by benchmarking weak funnel stages against the strongest
observed performance in the simulated dataset.

This makes the result a scenario estimate rather than
a claim of actual lost revenue.
"""


best_mql_to_sql = (
    channel_summary["mql_to_sql_pct"].max() / 100
)


best_opportunity_to_customer = (
    channel_summary["opportunity_to_customer_pct"].max() / 100
)


observed_mql_to_sql = sqls / mqls
observed_opportunity_to_customer = (
    customers / opportunities
)


# Potential SQLs if the MQL-to-SQL stage matched
# the best observed channel.

potential_sqls = round(mqls * best_mql_to_sql)

incremental_sqls = max(
    0,
    potential_sqls - sqls
)


# Preserve the observed SQL-to-opportunity rate.

sql_to_opportunity_rate = (
    opportunities / sqls
)


incremental_opportunities = round(
    incremental_sqls * sql_to_opportunity_rate
)


# Potential customers if Opportunity-to-Customer
# matched the best observed channel.

potential_customers = round(
    opportunities * best_opportunity_to_customer
)


incremental_customers = max(
    0,
    potential_customers - customers
)


# Average contract value among simulated customers.

average_customer_value = (
    df.loc[
        df["customer"] == 1,
        "estimated_acv"
    ].mean()
)


qualification_revenue_opportunity = (
    incremental_opportunities
    * average_customer_value
)


conversion_revenue_opportunity = (
    incremental_customers
    * average_customer_value
)


estimated_revenue_opportunity = (
    qualification_revenue_opportunity
    + conversion_revenue_opportunity
)


print("\nREVENUE LEAKAGE ANALYSIS")
print("-" * 70)

print(
    f"Best MQL → SQL benchmark: "
    f"{best_mql_to_sql * 100:.1f}%"
)

print(
    f"Observed MQL → SQL: "
    f"{observed_mql_to_sql * 100:.1f}%"
)

print(
    f"Qualification-stage revenue opportunity: "
    f"{money(qualification_revenue_opportunity)}"
)

print(
    f"Best Opportunity → Customer benchmark: "
    f"{best_opportunity_to_customer * 100:.1f}%"
)

print(
    f"Observed Opportunity → Customer: "
    f"{observed_opportunity_to_customer * 100:.1f}%"
)

print(
    f"Conversion-stage revenue opportunity: "
    f"{money(conversion_revenue_opportunity)}"
)

print(
    f"\nEstimated total revenue opportunity: "
    f"{money(estimated_revenue_opportunity)}"
)


# ============================================================
# 8. 90-DAY IMPROVEMENT SCENARIO
# ============================================================

"""
Scenario assumption:

Improve the two major bottlenecks by up to
10 percentage points, while never exceeding
the best observed conversion rate in the dataset.
"""


target_mql_to_sql = min(
    best_mql_to_sql,
    observed_mql_to_sql + 0.10
)


target_opportunity_to_customer = min(
    best_opportunity_to_customer,
    observed_opportunity_to_customer + 0.10
)


scenario_sqls = round(
    mqls * target_mql_to_sql
)


scenario_opportunities = round(
    scenario_sqls * sql_to_opportunity_rate
)


scenario_customers = round(
    scenario_opportunities
    * target_opportunity_to_customer
)


scenario_revenue = (
    scenario_customers
    * average_customer_value
)


incremental_revenue = (
    scenario_revenue
    - revenue
)


revenue_improvement = (
    incremental_revenue / revenue * 100
    if revenue > 0
    else 0
)


print("\n90-DAY GROWTH SCENARIO")
print("-" * 70)

print(
    f"Target MQL → SQL: "
    f"{target_mql_to_sql * 100:.1f}%"
)

print(
    f"Target Opportunity → Customer: "
    f"{target_opportunity_to_customer * 100:.1f}%"
)

print(
    f"Scenario Revenue: "
    f"{money(scenario_revenue)}"
)

print(
    f"Incremental Revenue: "
    f"{money(incremental_revenue)}"
)

print(
    f"Potential Revenue Improvement: "
    f"{revenue_improvement:.1f}%"
)


# ============================================================
# 9. EXECUTIVE TAKEAWAY
# ============================================================

print("\nEXECUTIVE TAKEAWAY")
print("-" * 70)

print(
    "The analysis suggests that the company should optimize "
    "existing funnel conversion before significantly increasing "
    "lead acquisition spend."
)

print(
    "Priority areas: lead qualification, marketing-to-sales "
    "handoff, follow-up speed, opportunity conversion, and "
    "channel-level budget allocation."
)

print("=" * 70)
