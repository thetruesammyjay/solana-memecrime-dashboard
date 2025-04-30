<template>
  <BaseCard v-if="cluster" class="p-4">
    <h3 class="text-sm font-semibold mb-2">Wallet Cluster</h3>
    <div class="flex items-center gap-2">
      <div 
        v-for="wallet in cluster.wallets.slice(0, 5)" 
        :key="wallet"
        class="w-6 h-6 rounded-full bg-solana-purple/20 flex items-center justify-center text-xs"
      >
        {{ wallet.slice(0, 2) }}
      </div>
      <span v-if="cluster.wallets.length > 5" class="text-xs text-gray-400">
        +{{ cluster.wallets.length - 5 }} more
      </span>
    </div>
  </BaseCard>
</template>

<script setup>
defineProps({
  cluster: {
    type: Object,
    default: null
  }
})
</script>