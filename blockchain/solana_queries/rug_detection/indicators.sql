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

holder_data AS (
  SELECT
    aa.token_mint_address,
    aa.token_balance_owner,
    SUM(aa.post_token_balance) AS balance
  FROM solana.account_activity aa
  JOIN new_tokens nt ON aa.token_mint_address = nt.token_mint_address
  WHERE aa.post_token_balance > 0
  GROUP BY 1, 2
  LIMIT 10000
),

metrics AS (
  SELECT
    token_mint_address,
    COUNT(DISTINCT token_balance_owner) AS holder_count,
    SUM(balance) AS total_supply,
    MAX(balance) / NULLIF(SUM(balance), 0) AS largest_holder_pct
  FROM holder_data
  GROUP BY 1
),

tx_metrics AS (
  SELECT
    aa.token_mint_address,
    COUNT(DISTINCT aa.tx_id) AS tx_count,
    COUNT(DISTINCT aa.token_balance_owner) AS unique_accounts
  FROM solana.account_activity aa
  JOIN new_tokens nt ON aa.token_mint_address = nt.token_mint_address
  WHERE aa.token_balance_change != 0
  GROUP BY 1
  LIMIT 5000
)

SELECT
  nt.token_mint_address,
  nt.creation_time,
  m.holder_count,
  m.largest_holder_pct * 100 AS largest_holder_percent,
  tx.tx_count,
  tx.unique_accounts,
  CASE
    WHEN m.largest_holder_pct > 0.9 THEN 'HIGH_RISK'
    WHEN m.largest_holder_pct > 0.7 THEN 'MEDIUM_RISK'
    ELSE 'LOW_RISK'
  END AS risk_level,
  CONCAT('https://solscan.io/token/', nt.token_mint_address) AS explorer_link
FROM new_tokens nt
LEFT JOIN metrics m ON nt.token_mint_address = m.token_mint_address
LEFT JOIN tx_metrics tx ON nt.token_mint_address = tx.token_mint_address
WHERE m.holder_count IS NOT NULL
ORDER BY risk_level, tx.tx_count DESC
LIMIT 100;