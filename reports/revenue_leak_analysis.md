# Revenue-leak analysis

## Method

The analysis compares each channel’s MQL-to-SQL conversion with the portfolio baseline. For underperforming channels, the recoverable opportunity is calculated as:

`MQL volume × conversion shortfall × average opportunity ARR × opportunity win rate`

This is deliberately conservative: it values only the incremental SQLs expected from bringing a channel to the portfolio baseline, then discounts them by that channel’s observed win rate. A separate response-time analysis compares SQL acceptance for MQLs handled inside and outside a 24-hour SLA.

## Findings

1. **Paid social is the highest-volume quality leak.** It creates substantial MQL volume but converts fewer MQLs to SQLs than the portfolio baseline. Refine job-function and company-size targeting, suppress low-intent audiences, and route uncertain prospects into a nurture sequence rather than immediately to sales.
2. **Response time is a controllable operational loss.** MQLs receiving first contact after 24 hours have lower sales acceptance. Put a monitored 24-hour SLA in place, use round-robin fallback, and alert managers when high-score leads age past four business hours.
3. **Webinars need stronger post-event qualification.** Their MQL rate is healthy; the sales handoff is not. Score attendance, questions, and pricing-page activity before handoff, then use an SDR follow-up playbook for high-intent attendees.

## How to read the estimate

The dashboard and `outputs/summary.json` contain the exact values generated from the included deterministic data. The annualized label assumes the observed cohort is representative of a year’s acquisition mix. This is a planning estimate—not booked revenue—and should be validated with CRM opportunity outcomes, attribution rules, and sales-capacity constraints.
