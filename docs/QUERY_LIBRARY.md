# Solana Query Library

## Token Analysis

### `launches.sql`
```sql
-- New token launches with liquidity info
WITH new_tokens AS (
    SELECT token_address, name, symbol, MIN(block_time) as launch_time
    FROM solana.token_mints 
    GROUP BY 1,2,3
)
SELECT nt.*, lp.initial_liquidity
FROM new_tokens nt
LEFT JOIN liquidity_pools lp ON nt.token_address = lp.token_address
```
**Purpose**: Track new token launches with initial liquidity

**Columns**:
- token_address: On-chain address

- launch_time: First mint timestamp

- initial_liquidity: USD value of starting liquidity


### `liquidity.sql`
```sql
-- Liquidity changes over time
SELECT 
    token_address,
    block_time,
    action,
    amount_usd,
    SUM(CASE WHEN action = 'add' THEN amount_usd ELSE -amount_usd END) 
        OVER (PARTITION BY token_address ORDER BY block_time) as net_liquidity
FROM solana.liquidity_pool_actions
```

**Purpose**: Monitor liquidity additions/removals

**Key Metrics**:

`net_liquidity`: Running total of pool liquidity

`action`: 'add' or 'remove'

---
## Wallet Analysis
### `clustering.sql`
```sql
-- Wallet interaction clustering
WITH interactions AS (
    SELECT from, to, COUNT(*) as tx_count
    FROM solana.transfers
    GROUP BY 1,2
    HAVING COUNT(*) > 3
)
SELECT 
    node,
    DENSE_RANK() OVER (ORDER BY component) as cluster_id
FROM (
    SELECT node, component
    FROM graph_analysis(interactions)
)
```

**Purpose**: Identify connected wallet groups

**Method**: Graph analysis of transaction patterns

### `market-makers.sql`
```sql
-- High-frequency traders
SELECT 
    wallet,
    COUNT(DISTINCT token) as tokens_traded,
    COUNT(*) as trades,
    SUM(amount_usd) as volume
FROM solana.trades
WHERE block_time > NOW() - INTERVAL '1 day'
GROUP BY 1
HAVING COUNT(*) > 50
ORDER BY 4 DESC
```
**Purpose**: Detect market maker activity
**Threshold**:
- | 50 trades/day
- | $10k volume

---

## Rug Detection
### `indicators.sql`
```sql
-- Composite rug pull signals
SELECT
    token_address,
    MAX(liquidity_removed) as liquidity_drop,
    MAX(price_drop) as price_drop,
    CASE
        WHEN liquidity_drop > 0.8 AND price_drop > 0.9 THEN 'CONFIRMED_RUG'
        WHEN liquidity_drop > 0.5 THEN 'SUSPICIOUS'
        ELSE 'CLEAN'
    END as status
FROM (
    -- Subquery with token metrics
)
GROUP BY 1
```

**Key Indicators**:

1. 80% liquidity removal

2. 90% price drop

3. Creator wallet sells

---

## Query Performance
| Query           | Execution Time | Frequency       |
|----------------|----------------|-----------------|
| launches.sql    | 15s            | Hourly          |
| liquidity.sql   | 30s            | Every 5 mins    |
| clustering.sql  | 2m             | Daily           |

**Optimization Tips**:

1. Use `PARTITION` BY for time-series data

2. Materialize frequently used views

3. Limit historical data with `block_time` filters
