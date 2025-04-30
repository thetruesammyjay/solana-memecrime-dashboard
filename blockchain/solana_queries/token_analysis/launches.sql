WITH recent_launches AS (
  SELECT DISTINCT
    address AS token_address,
    MIN(block_time) AS creation_time,
    FIRST_VALUE(symbol) OVER (PARTITION BY address ORDER BY block_time) AS symbol,
    FIRST_VALUE(decimals) OVER (PARTITION BY address ORDER BY block_time) AS decimals,
    FIRST_VALUE(signer) OVER (PARTITION BY address ORDER BY block_time) AS deployer
  FROM solana.token_creations
  WHERE block_time >= NOW() - INTERVAL '3 days'
  GROUP BY address, symbol, decimals, signer, block_time
  LIMIT 1000
),

deployer_stats AS (
  SELECT
    signer AS deployer,
    COUNT(DISTINCT address) AS token_count
  FROM solana.token_creations
  WHERE block_time >= NOW() - INTERVAL '7 days'
  GROUP BY signer
  LIMIT 500
)

SELECT
  rl.token_address,
  rl.symbol,
  rl.deployer,
  rl.creation_time,
  COALESCE(ds.token_count, 1) AS deployer_activity_count,
  CASE
    WHEN COALESCE(ds.token_count, 1) > 5 THEN 'SERIAL_DEPLOYER'
    WHEN COALESCE(ds.token_count, 1) > 2 THEN 'SUSPECT_DEPLOYER'
    ELSE 'NEW_DEPLOYER'
  END AS deployer_risk_profile
FROM recent_launches rl
LEFT JOIN deployer_stats ds ON rl.deployer = ds.deployer
ORDER BY rl.creation_time DESC
LIMIT 100;