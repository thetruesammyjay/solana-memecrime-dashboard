WITH new_tokens AS (
  SELECT DISTINCT
    token_mint_address,
    MIN(block_time) AS creation_time
  FROM solana.account_activity
  WHERE 
    block_time >= CURRENT_DATE - INTERVAL '7' day
    AND token_mint_address IS NOT NULL
  GROUP BY 1
  LIMIT 1000
),

liquidity_events AS (
  SELECT
    aa.token_mint_address,
    aa.token_balance_owner AS lp_provider,
    aa.token_balance_change,
    aa.post_token_balance,
    CASE WHEN aa.token_balance_change > 0 THEN 'ADD' ELSE 'REMOVE' END AS event_type
  FROM solana.account_activity aa
  JOIN new_tokens nt ON aa.token_mint_address = nt.token_mint_address
  WHERE aa.token_balance_change != 0
  LIMIT 5000
),

lp_metrics AS (
  SELECT
    token_mint_address,
    SUM(CASE WHEN event_type = 'ADD' THEN ABS(token_balance_change) ELSE 0 END) AS total_added,
    SUM(CASE WHEN event_type = 'REMOVE' THEN ABS(token_balance_change) ELSE 0 END) AS total_removed,
    COUNT(DISTINCT CASE WHEN event_type = 'ADD' THEN lp_provider END) AS unique_adders,
    MAX(CASE WHEN event_type = 'ADD' THEN post_token_balance ELSE 0 END) / 
      NULLIF(SUM(CASE WHEN event_type = 'ADD' THEN post_token_balance ELSE 0 END), 0) AS largest_lp_pct
  FROM liquidity_events
  GROUP BY 1
)

SELECT
  nt.token_mint_address,
  nt.creation_time,
  lp.total_added,
  lp.total_removed,
  lp.unique_adders,
  lp.largest_lp_pct * 100 AS largest_lp_percent,
  (lp.total_removed / NULLIF(lp.total_added, 0)) * 100 AS percent_removed,
  CASE
    WHEN lp.largest_lp_pct > 0.9 OR (lp.total_removed / NULLIF(lp.total_added, 0)) > 0.8 THEN 'HIGH_RISK'
    WHEN lp.largest_lp_pct > 0.7 OR (lp.total_removed / NULLIF(lp.total_added, 0)) > 0.5 THEN 'MEDIUM_RISK'
    ELSE 'LOW_RISK'
  END AS risk_level,
  CONCAT('https://solscan.io/token/', nt.token_mint_address) AS explorer_link
FROM new_tokens nt
LEFT JOIN lp_metrics lp ON nt.token_mint_address = lp.token_mint_address
WHERE lp.total_added IS NOT NULL
ORDER BY risk_level, lp.total_added DESC
LIMIT 100;