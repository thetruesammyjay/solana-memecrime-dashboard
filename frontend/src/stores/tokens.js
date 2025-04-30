import { defineStore } from 'pinia'
import { ref } from 'vue'
import { Connection, PublicKey } from '@solana/web3.js'

export const useTokenStore = defineStore('tokens', () => {
  const connection = new Connection('https://api.mainnet-beta.solana.com')
  const tokens = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchRecentTokens(limit = 50) {
    loading.value = true
    try {
      // Fetch trending tokens from Jupiter API
      const response = await fetch('https://token-api.jup.ag/api/v1/tokens')
      const allTokens = await response.json()
      
      // Get top tokens by volume
      const trending = Object.values(allTokens)
        .sort((a, b) => b.volume24h - a.volume24h)
        .slice(0, limit)

      // Enrich with on-chain data
      tokens.value = await Promise.all(
        trending.map(async token => {
          const accountInfo = await connection.getParsedAccountInfo(new PublicKey(token.address))
          return {
            ...token,
            supply: accountInfo.value?.data?.parsed?.info?.supply,
            risk: await calculateRisk(token.address)
          }
        })
      )
    } catch (err) {
      error.value = `Failed to fetch tokens: ${err.message}`
    } finally {
      loading.value = false
    }
  }

  async function calculateRisk(tokenAddress) {
    try {
      const [liquidityRes, holdersRes] = await Promise.all([
        fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`),
        fetch(`https://api.solscan.io/token/holders?token=${tokenAddress}&limit=10`)
      ])
      
      const liquidityData = await liquidityRes.json()
      const holdersData = await holdersRes.json()

      // Risk calculation logic
      const topHolderPct = holdersData.data[0]?.amount / holdersData.totalSupply * 100
      const liquidityChanges = liquidityData.pairs[0]?.priceChange?.h24

      return {
        level: topHolderPct > 50 ? 'critical' : 
               liquidityChanges < -30 ? 'high' : 'medium',
        reasons: [
          ...(topHolderPct > 30 ? [`Top holder owns ${topHolderPct.toFixed(2)}%`] : []),
          ...(liquidityChanges < -20 ? [`24h liquidity drop: ${liquidityChanges.toFixed(2)}%`] : [])
        ]
      }
    } catch {
      return { level: 'unknown', reasons: [] }
    }
  }

  return { 
    tokens, 
    loading, 
    error,
    fetchRecentTokens
  }
})