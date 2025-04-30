<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex items-center mb-10">
      <img src="/solana-icon.svg" alt="Solana Logo" class="w-10 h-10 mr-4" />
      <h1 class="text-3xl font-bold text-white">MemeCrime Dashboard</h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Overview Stats -->
      <div class="lg:col-span-3 grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Tokens Tracked" :value="tokenStore.tokens.length" />
        <StatCard title="Active Alerts" :value="alertStore.alerts.length" variant="warning" />
        <StatCard title="High Risk" :value="highRiskCount" variant="danger" />
        <WalletButton />
      </div>

      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-8">
        <div class="card-glass p-6">
          <h2 class="text-2xl font-semibold mb-4">Trending Tokens</h2>
          <TokenList />
        </div>

        <div class="card-glass p-6">
          <h2 class="text-2xl font-semibold mb-4">Liquidity Flows</h2>
          <LiquiditySankey :data="sankeyData" />
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-8">
        <div class="card-glass p-6">
          <h2 class="text-2xl font-semibold mb-4">Recent Alerts</h2>
          <AlertFeed />
        </div>

        <div v-if="walletStore.publicKey" class="card-glass p-6">
          <h2 class="text-2xl font-semibold mb-4">Wallet Cluster</h2>
          <WalletCluster />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// STORES
import { useTokenStore, useAlertsStore, useWalletStore } from '@/stores'

// COMPONENTS
import TokenList from '@/components/tokens/TokenList.vue'
import LiquiditySankey from '@/components/charts/LiquiditySankey.vue'
import AlertFeed from '@/components/alerts/AlertFeed.vue'
import WalletButton from '@/components/wallet/WalletButton.vue'
import WalletCluster from '@/components/wallet/WalletCluster.vue'
import StatCard from '@/components/ui/BaseCard.vue' // We'll reuse BaseCard for now!

const tokenStore = useTokenStore()
const alertStore = useAlertsStore()
const walletStore = useWalletStore()

const highRiskCount = computed(() => {
  return tokenStore.tokens.filter(t => 
    t.risk.level === 'high' || t.risk.level === 'critical'
  ).length
})

const sankeyData = computed(() => ({
  nodes: [
    { name: 'Creator', color: '#EF4444' },
    { name: 'LP Pool', color: '#3B82F6' },
    { name: 'CEX', color: '#10B981' }
  ],
  links: [
    { source: 0, target: 1, value: 1000000 },
    { source: 1, target: 2, value: 800000 }
  ]
}))

// Fetch initial data
tokenStore.fetchRecentTokens()
alertStore.fetchAlerts()
</script>
