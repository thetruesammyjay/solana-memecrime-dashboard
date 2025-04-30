import { ref, onUnmounted } from 'vue'
import { Connection, PublicKey } from '@solana/web3.js'
import { RateLimiter } from 'limiter'

// Initialize rate limiter (10 requests/second)
const limiter = new RateLimiter({
  tokensPerInterval: 10,
  interval: 'second'
})

// Cache setup with 5-minute TTL
const cache = new Map()
const CACHE_TTL = 300000 // 5 minutes

const SOL_MINT = 'So11111111111111111111111111111111111111112'

export function useChainData() {
  const connection = new Connection('https://api.mainnet-beta.solana.com')
  const loading = ref(false)
  const error = ref(null)
  const realTimeUpdates = ref([])
  let wsConnection = null

  // WebSocket cleanup on unmount
  onUnmounted(() => {
    if (wsConnection) {
      wsConnection.close()
    }
  })

  /**
   * Cached fetch with rate limiting
   */
  async function cachedFetch(url) {
    await limiter.removeTokens(1) // Rate limiting
    
    // Check cache first
    const cached = cache.get(url)
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.data
    }

    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP error: ${res.status}`)
    
    const data = await res.json()
    cache.set(url, { data, timestamp: Date.now() })
    return data
  }

  /**
   * Initialize WebSocket for real-time liquidity updates
   */
  function initWebSocket(tokenAddress) {
    if (wsConnection) wsConnection.close()

    wsConnection = new WebSocket('wss://api.mainnet-beta.solana.com')

    wsConnection.onopen = () => {
      wsConnection.send(JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'accountSubscribe',
        params: [
          new PublicKey(tokenAddress).toBase58(),
          { encoding: 'jsonParsed', commitment: 'confirmed' }
        ]
      }))
    }

    wsConnection.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.params?.result) {
        realTimeUpdates.value = [
          ...realTimeUpdates.value.slice(-9), // Keep last 10 updates
          {
            timestamp: Date.now(),
            value: data.params.result.value.data.parsed.info.supply
          }
        ]
      }
    }
  }

  /**
   * Enhanced liquidity data with real-time updates
   */
  async function fetchLiquidityData(tokenAddress) {
    loading.value = true
    try {
      initWebSocket(tokenAddress)
      
      const [quote, routes] = await Promise.all([
        cachedFetch(`https://quote-api.jup.ag/v6/quote?inputMint=${tokenAddress}&outputMint=${SOL_MINT}&amount=1000000`),
        cachedFetch('https://quote-api.jup.ag/v6/route-map')
      ])

      return {
        price: quote.outAmount / (10 ** quote.outputDecimals),
        priceImpact: quote.priceImpactPct,
        availableRoutes: routes.filter(r => 
          r.inputMint === tokenAddress || r.outputMint === tokenAddress
        ),
        realTimeUpdates
      }
    } catch (err) {
      error.value = `Liquidity fetch failed: ${err.message}`
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Get token metadata with cache
   */
  async function fetchTokenData(tokenAddress) {
    const cacheKey = `token-${tokenAddress}`
    if (cache.has(cacheKey)) return cache.get(cacheKey).data

    loading.value = true
    try {
      const accountInfo = await connection.getParsedAccountInfo(new PublicKey(tokenAddress))
      const data = {
        supply: accountInfo.value?.data?.parsed?.info?.supply,
        decimals: accountInfo.value?.data?.parsed?.info?.decimals,
        mintAuthority: accountInfo.value?.data?.parsed?.info?.mintAuthority
      }
      cache.set(cacheKey, { data, timestamp: Date.now() })
      return data
    } catch (err) {
      error.value = `Token data error: ${err.message}`
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Rug pull detection with multiple indicators
   */
  async function checkRugIndicators(tokenAddress) {
    const [tokenData, liquidityData] = await Promise.all([
      fetchTokenData(tokenAddress),
      fetchLiquidityData(tokenAddress)
    ])

    // Analyze real-time updates for sudden drops
    const liquidityChanges = realTimeUpdates.value
    const suddenDrop = liquidityChanges.length > 3 && 
      liquidityChanges.slice(-1)[0].value < liquidityChanges[0].value * 0.7

    return {
      suddenLiquidityDrop: suddenDrop,
      concentratedRoutes: liquidityData?.availableRoutes?.length < 2,
      activeMintAuthority: tokenData?.mintAuthority !== null,
      highPriceImpact: liquidityData?.priceImpact > 0.05 // 5%
    }
  }

  return {
    loading,
    error,
    realTimeUpdates,
    fetchTokenData,
    fetchLiquidityData,
    checkRugIndicators
  }
}