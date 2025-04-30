-- Market maker detection via trading patterns
WITH trader_stats AS (
    SELECT
        tx_from as trader_address,
        COUNT(DISTINCT token_address) as tokens_traded,
        COUNT(*) as total_trades,
        SUM(amount_usd) as total_volume,
        AVG(amount_usd) as avg_trade_size,
        MIN(block_time) as first_trade,
        MAX(block_time) as last_trade,
        EXTRACT(EPOCH FROM (MAX(block_time) - MIN(block_time))) / 3600 as trading_hours,
        COUNT(*) / NULLIF(EXTRACT(EPOCH FROM (MAX(block_time) - MIN(block_time))) / 3600, 0) as trades_per_hour
    FROM solana.token_transfers
    WHERE block_time >= NOW() - INTERVAL '7 days'
    AND transfer_type = 'TRADE'
    GROUP BY 1
    HAVING COUNT(*) > 50
)

SELECT
    ts.*,
    (SELECT COUNT(DISTINCT DATE_TRUNC('hour', block_time)) 
        FROM solana.token_transfers tt 
        WHERE tt.tx_from = ts.trader_address) as active_hours,
    (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount_usd) 
        FROM solana.token_transfers tt 
        WHERE tt.tx_from = ts.trader_address) as median_trade_size,
    CASE
        WHEN trades_per_hour > 30 AND avg_trade_size < 100 THEN 'LIKELY_BOT'
        WHEN tokens_traded > 20 AND trading_hours < 24 THEN 'PUMP_GROUP'
        WHEN total_volume > 100000 AND trades_per_hour > 10 THEN 'MARKET_MAKER'
        ELSE 'UNKNOWN'
    END as trader_type
FROM trader_stats ts
ORDER BY total_volume DESC
LIMIT 500;