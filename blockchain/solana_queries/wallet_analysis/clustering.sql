-- Wallet Clustering with Transaction Pattern Analysis
WITH deployer_clusters AS (
  SELECT
    signer AS deployer,
    COUNT(DISTINCT address) AS token_count,
    ARRAY_AGG(DISTINCT address) AS tokens_created,
    MIN(block_time) AS first_activity,
    MAX(block_time) AS last_activity
  FROM solana.token_creations
  GROUP BY 1
),

wallet_transactions AS (
  SELECT
    dc.deployer,
    COUNT(DISTINCT tr.tx_hash) AS total_txs,
    COUNT(DISTINCT CASE WHEN tr.block_time <= tc.block_time + INTERVAL '1 hour' THEN tr.tx_hash END) AS first_hour_txs,
    COUNT(DISTINCT tr.from_address) AS unique_counterparties
  FROM deployer_clusters dc
  JOIN solana.token_creations tc ON dc.deployer = tc.signer
  LEFT JOIN solana.token_transfers tr ON tc.address = tr.token_address
  GROUP BY 1
)

SELECT
  dc.deployer,
  dc.token_count,
  dc.first_activity,
  dc.last_activity,
  wt.total_txs,
  wt.first_hour_txs,
  wt.unique_counterparties,
  wt.first_hour_txs / NULLIF(wt.total_txs, 0) AS early_activity_ratio,
  CASE
    WHEN dc.token_count > 5 AND wt.early_activity_ratio > 0.7 THEN 'HIGH_RISK_CLUSTER'
    WHEN dc.token_count > 2 AND wt.early_activity_ratio > 0.5 THEN 'MEDIUM_RISK_CLUSTER'
    ELSE 'LOW_RISK_CLUSTER'
  END AS cluster_risk_profile
FROM deployer_clusters dc
JOIN wallet_transactions wt ON dc.deployer = wt.deployer
ORDER BY dc.token_count DESC, wt.early_activity_ratio DESC