<template>
  <div class="container mx-auto px-4 py-6">
    <div v-if="wallet" class="space-y-6">
      <!-- Wallet Header -->
      <div class="p-4 bg-gray-800 rounded-lg">
        <h1 class="text-xl font-bold">Wallet Investigator</h1>
        <p class="font-mono text-sm text-gray-400">{{ wallet.address }}</p>
      </div>

      <!-- Cluster Analysis -->
      <WalletCluster :cluster="cluster" />

      <!-- Token Holdings -->
      <TokenList :tokens="wallet.tokens" />

      <!-- Transaction Network -->
      <TokenNetwork :nodes="nodes" :links="links" />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()
const wallet = ref({
  address: route.params.address,
  tokens: [] // Would be populated from API
})

const cluster = ref({
  id: 1,
  wallets: ['Wallet1', 'Wallet2', 'Wallet3', 'Wallet4', 'Wallet5']
})

const nodes = ref([
  { id: wallet.value.address, group: 1 },
  { id: 'TokenA', group: 2 },
  { id: 'TokenB', group: 2 }
])

const links = ref([
  { source: wallet.value.address, target: 'TokenA', value: 5 },
  { source: wallet.value.address, target: 'TokenB', value: 3 }
])
</script>