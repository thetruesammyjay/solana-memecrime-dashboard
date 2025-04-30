<template>
  <div class="container mx-auto px-4 py-6">
    <template v-if="loading">
      <div class="flex justify-center py-12">
        <BaseSpinner size="lg" />
      </div>
    </template>

    <template v-else-if="token">
      <!-- Token Header -->
      <div class="flex items-center justify-between mb-8 p-4 bg-gray-800 rounded-lg">
        <div class="flex items-center gap-4">
          <TokenIcon :token="token" size="lg" />
          <div>
            <h1 class="text-2xl font-bold">{{ token.name }}</h1>
            <div class="flex items-center gap-2">
              <span class="font-mono text-sm text-gray-400">{{ shortAddress(token.address) }}</span>
              <CopyButton :text="token.address" />
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <RiskBadge :level="token.risk.level" />
          <WatchlistButton :tokenAddress="token.address" />
        </div>
      </div>

      <!-- Main Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left Column -->
        <div class="lg:col-span-2 space-y-6">
          <TokenMetrics 
            :price="token.price" 
            :liquidity="token.liquidity"
            :volume="token.volume24h"
          />
          
          <LiquidityChart 
            :history="liquidityHistory"
            :real-time="realTimeUpdates"
          />
          
          <TransactionHistory 
            :address="token.address"
            class="h-96"
          />
        </div>

        <!-- Right Column -->
        <div class="space-y-6">
          <TokenHolders 
            :holders="token.holders"
            :supply="token.supply"
          />
          
          <RugPullIndicators 
            :indicators="token.risk"
            class="sticky top-4"
          />
          
          <RelatedTokens 
            v-if="similarTokens.length"
            :tokens="similarTokens"
          />
        </div>
      </div>
    </template>

    <BaseDialog v-else title="Token Not Found">
      <p>The requested token could not be loaded.</p>
      <RouterLink 
        to="/" 
        class="mt-4 inline-block text-solana-green hover:underline"
      >
        Back to Dashboard
      </RouterLink>
    </BaseDialog>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useTokenStore } from '@/stores/tokens'
import { useChainData } from '@/composables/useChainData'

const route = useRoute()
const tokenStore = useTokenStore()
const { realTimeUpdates, fetchLiquidityData } = useChainData()

const token = ref(null)
const loading = ref(false)
const similarTokens = ref([])

const liquidityHistory = computed(() => {
  return [
    { time: '24h ago', value: token.value?.liquidity * 1.2 },
    { time: '12h ago', value: token.value?.liquidity * 1.1 },
    { time: 'Now', value: token.value?.liquidity }
  ]
})

watch(() => route.params.address, async (newAddress) => {
  if (newAddress) {
    loading.value = true
    try {
      // Fetch token data
      const [jupiterData, dexScreenerData] = await Promise.all([
        fetch(`https://token-api.jup.ag/api/v1/tokens/${newAddress}`).then(r => r.json()),
        fetch(`https://api.dexscreener.com/latest/dex/tokens/${newAddress}`).then(r => r.json())
      ])

      token.value = {
        ...jupiterData,
        ...dexScreenerData.pairs[0],
        address: newAddress,
        risk: await tokenStore.calculateRisk(newAddress)
      }

      // Fetch similar tokens
      similarTokens.value = await tokenStore.fetchSimilarTokens(newAddress)
      
      // Start real-time monitoring
      fetchLiquidityData(newAddress)
    } catch (err) {
      console.error('Failed to load token:', err)
    } finally {
      loading.value = false
    }
  }
}, { immediate: true })

function shortAddress(address) {
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}
</script>