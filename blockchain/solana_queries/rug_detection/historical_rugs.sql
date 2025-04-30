-- Historical rug patterns for machine learning
WITH confirmed_rugs AS (
    SELECT DISTINCT token_address
    FROM solana.rug_pulls -- Assuming you have a table of known rug pulls
    WHERE confirmed = true
),

rug_metrics AS (
    SELECT
        r.token_address,
        t.token_name,
        t.token_symbol,
        t.launch_time,
        EXTRACT(EPOCH FROM (rp.rug_time - t.launch_time)) / 3600 as hours_to_rug,
        rp.amount_stolen_usd,
        (SELECT COUNT(*) FROM solana.token_transfers tt 
         WHERE tt.token_address = r.token_address
         AND tt.block_time BETWEEN t.launch_time AND rp.rug_time) as pre_rug_txs,
        (SELECT COUNT(DISTINCT tt.tx_from) FROM solana.token_transfers tt 
         WHERE tt.token_address = r.token_address
         AND tt.block_time BETWEEN t.launch_time AND rp.rug_time) as unique_traders,
        (SELECT MAX(lp.amount_usd) FROM solana.liquidity_pool_actions lp 
         WHERE lp.token_address = r.token_address
         AND lp.block_time BETWEEN t.launch_time AND rp.rug_time
         AND lp.action = 'add') as peak_liquidity
    FROM confirmed_rugs r
    JOIN solana.tokens t ON r.token_address = t.token_address
    JOIN solana.rug_pulls rp ON r.token_address = rp.token_address
)

SELECT 
    rm.*,
    (SELECT ARRAY_AGG(wallet_address) FROM (
        SELECT wallet_address FROM solana.token_balances tb
        WHERE tb.token_address = rm.token_address
        AND tb.block_time = (
            SELECT MAX(block_time) 
            FROM solana.token_balances 
            WHERE token_address = rm.token_address 
            AND block_time <= rm.rug_time)
        ORDER BY balance DESC
        LIMIT 5
    ) top_holders) as top_holders_at_rug,
    (SELECT STRING_AGG(action || ':' || amount_usd::TEXT, ',') FROM (
        SELECT action, SUM(amount_usd) as amount_usd
        FROM solana.liquidity_pool_actions
        WHERE token_address = rm.token_address
        AND block_time BETWEEN rm.launch_time AND rm.rug_time
        GROUP BY action
    ) lp_actions) as liquidity_changes
FROM rug_metrics rm
ORDER BY hours_to_rug ASC;