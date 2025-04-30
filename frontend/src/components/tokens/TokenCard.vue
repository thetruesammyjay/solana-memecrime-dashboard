<template>
  <BaseCard class="hover:bg-gray-800 transition-colors cursor-pointer">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-full bg-solana-purple/20 flex items-center justify-center">
        <span class="text-xs">{{ token.symbol?.slice(0, 3) }}</span>
      </div>
      <div class="flex-1">
        <h3 class="font-medium">{{ token.name }}</h3>
        <p class="text-xs text-gray-400">{{ token.address.slice(0, 6) }}...{{ token.address.slice(-4) }}</p>
      </div>
      <RiskBadge :level="token.risk.level" />
    </div>
  </BaseCard>
</template>

<script setup>
import RiskBadge from './RiskBadge.vue'
import BaseCard from '@/components/ui/BaseCard.vue'

defineProps({
  token: {
    type: Object,
    required: true
  }
})
</script>