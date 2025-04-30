<template>
  <div class="space-y-2">
    <div class="flex justify-between items-center">
      <h3 class="font-semibold">Recent Tokens</h3>
      <span class="text-xs text-gray-400">{{ tokens.length }} total</span>
    </div>
    <div v-if="loading" class="flex justify-center py-4">
      <BaseSpinner />
    </div>
    <div v-else class="space-y-2">
      <TokenCard 
        v-for="token in tokens" 
        :key="token.address" 
        :token="token" 
      />
    </div>
  </div>
</template>

<script setup>
import { useTokenStore } from '@/stores/tokens'
import { storeToRefs } from 'pinia'

const { tokens, loading } = storeToRefs(useTokenStore())
</script>