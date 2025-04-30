 API Specification

## Base URL
`https://api.memecrime.com/v1`

## Authentication
```http
GET /endpoint
Authorization: Bearer <jwt_token>
```

## Endpoint
### Tokens

**Get Token Details**
```http
GET /tokens/{token_address}
```
**Response**:
```json
{
  "token": {
    "address": "EPjFWdd5...",
    "name": "USD Coin",
    "symbol": "USDC",
    "launch_time": "2023-01-01T00:00:00Z"
  },
  "risk": {
    "score": 0.87,
    "level": "high",
    "indicators": ["liquidity_removal", "creator_dumping"]
  }
}
```

**Get token transactions**:
```http
GET /tokens/{token_address}/transactions?timeframe=24&limit=100
```
**Paremeters**:
- `timeframe`: Hours to look back (default: 24)

- `limit`: Max transactions to return (default: 100)

### Wallets

**Get Wallet Details**
```http
GET /wallets/{wallet_address}
```
**Response**:
```json
{
  "wallet": "F5v4...",
  "cluster": {
    "id": 42,
    "size": 15,
    "volume": 250000
  },
  "risk": {
    "score": -0.65,
    "type": "market_maker"
  }
}
```

### Alerts

**Create Token Alert**
```http
POST /tokens/{token_address}/watch
{
  "alert_type": "risk_score",
  "threshold": 0.8
}
```

**List Active Alerts**
```http
GET /alerts?timeframe=24&type=token
```

## Error Codes
| Code | Meaning                  |
|------|--------------------------|
| 400  | Invalid request parameters |
| 401  | Unauthorized             |
| 404  | Resource not found       |
| 429  | Rate limit exceeded      |
| 500  | Internal server error    |

## Rate Limits
- 100 requests/minute per API key

- 5 concurrent requests