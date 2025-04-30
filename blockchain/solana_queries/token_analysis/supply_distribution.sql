-- Token supply concentration analysis
WITH token_holders AS (
    SELECT
        token_address,
        wallet_address,
        balance,
        balance / SUM(balance) OVER (PARTITION BY token_address) * 100 as pct_supply,
        ROW_NUMBER() OVER (PARTITION BY token_address ORDER BY balance DESC) as holder_rank
    FROM solana.token_balances
    WHERE block_time = (SELECT MAX(block_time) FROM solana.token_balances)
),  
  
SELECT
    th.token_address,
    t.token_name,
    t.token_symbol,
    th.wallet_address,
    th.balance,
    th.pct_supply,
    th.holder_rank,
    CASE 
        WHEN th.holder_rank = 1 AND th.pct_supply > 50 THEN 'CREATOR_DOMINANCE'
        WHEN th.holder_rank <= 5 AND th.pct_supply > 90 THEN 'CENTRALIZED'
        WHEN th.holder_rank <= 10 AND th.pct_supply > 95 THEN 'HIGHLY_CENTRALIZED'
        ELSE 'DISTRIBUTED'
    END as concentration_status,
    COUNT(*) OVER (PARTITION BY th.token_address) as unique_holders
FROM token_holders th
JOIN solana.tokens t ON th.token_address = t.token_address
WHERE th.holder_rank <= 20
ORDER BY th.token_address, th.holder_rank;