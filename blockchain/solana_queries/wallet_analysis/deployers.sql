-- Token deployers with activity patterns
WITH token_deployers AS (
    SELECT 
        tx_signer as deployer_address,
        COUNT(DISTINCT token_address) as tokens_created,
        MIN(block_time) as first_deploy,
        MAX(block_time) as last_deploy,
        AVG(EXTRACT(EPOCH FROM (MAX(block_time) - MIN(block_time)) / 3600 as avg_deploy_interval_hours))
    FROM solana.token_mints
    WHERE block_time >= NOW() - INTERVAL '30 days'
    GROUP BY 1
    HAVING COUNT(DISTINCT token_address) > 1
),

deployer_activity AS (
    SELECT
        td.*,
        (SELECT COUNT(*) FROM solana.liquidity_pool_actions lpa 
         WHERE lpa.liquidity_provider = td.deployer_address
         AND lpa.action = 'remove'
         AND lpa.block_time >= NOW() - INTERVAL '30 days') as lp_removals,
        (SELECT SUM(amount_usd) FROM solana.token_transfers tt 
         WHERE tt.tx_from = td.deployer_address
         AND tt.transfer_type = 'SELL'
         AND tt.block_time >= NOW() - INTERVAL '30 days') as total_sells_usd
    FROM token_deployers td
)

SELECT
    da.*,
    CASE
        WHEN da.lp_removals > 3 AND da.total_sells_usd > 10000 THEN 'HIGH_RISK'
        WHEN da.lp_removals > 1 AND da.total_sells_usd > 5000 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END as risk_category,
    (SELECT ARRAY_AGG(token_address) FROM solana.token_mints tm 
     WHERE tm.tx_signer = da.deployer_address
     AND tm.block_time >= NOW() - INTERVAL '30 days') as deployed_tokens
FROM deployer_activity da
ORDER BY da.total_sells_usd DESC
LIMIT 200;