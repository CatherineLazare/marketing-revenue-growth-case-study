-- SQLite: load data/leads.csv into a table called leads before running.
-- Channel funnel performance
SELECT channel, COUNT(*) AS leads,
  SUM(mql_date <> '') AS mqls, SUM(sql_date <> '') AS sqls,
  SUM(opportunity_date <> '') AS opportunities, SUM(customer_date <> '') AS customers,
  ROUND(100.0 * SUM(mql_date <> '') / COUNT(*), 1) AS lead_to_mql_pct,
  ROUND(100.0 * SUM(sql_date <> '') / NULLIF(SUM(mql_date <> ''), 0), 1) AS mql_to_sql_pct,
  ROUND(SUM(CAST(expected_arr AS REAL)), 0) AS pipeline_arr
FROM leads GROUP BY channel ORDER BY pipeline_arr DESC;

-- Sales response-time leak: compare MQL acceptance above vs. within a 24-hour SLA.
SELECT CASE WHEN CAST(first_response_hours AS REAL) <= 24 THEN 'Within 24 hours' ELSE 'Over 24 hours' END AS response_sla,
  COUNT(*) AS mqls, SUM(sql_date <> '') AS sqls,
  ROUND(100.0 * SUM(sql_date <> '') / COUNT(*), 1) AS mql_to_sql_pct
FROM leads WHERE mql_date <> '' GROUP BY response_sla;

-- Prioritize campaigns with material volume and below-average MQL-to-SQL conversion.
WITH benchmark AS (SELECT AVG(channel_rate) AS avg_rate FROM (
  SELECT 1.0 * SUM(sql_date <> '') / SUM(mql_date <> '') AS channel_rate FROM leads GROUP BY channel
))
SELECT campaign, channel, COUNT(*) AS leads, SUM(mql_date <> '') AS mqls,
  ROUND(100.0 * SUM(sql_date <> '') / NULLIF(SUM(mql_date <> ''),0),1) AS mql_to_sql_pct
FROM leads GROUP BY campaign, channel
HAVING SUM(mql_date <> '') >= 50
ORDER BY mql_to_sql_pct ASC;
