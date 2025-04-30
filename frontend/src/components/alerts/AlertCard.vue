<template>
  <BaseCard class="border-l-4" :class="alertBorderClass">
    <div class="flex items-start gap-3">
      <div class="flex-1">
        <h3 class="font-mono text-sm">{{ alert.tokenSymbol }}</h3>
        <p class="text-xs opacity-80">{{ alert.message }}</p>
      </div>
      <span class="text-xs">{{ timeAgo }}</span>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from '@/components/ui/BaseCard.vue'

const props = defineProps({
  alert: {
    type: Object,
    required: true
  }
})

const alertBorderClass = computed(() => {
  return {
    'border-red-500': props.alert.severity === 'critical',
    'border-orange-400': props.alert.severity === 'warning',
    'border-yellow-300': props.alert.severity === 'info'
  }
})

const timeAgo = computed(() => {
  const minutes = Math.floor((Date.now() - new Date(props.alert.timestamp)) / 60000)
  return `${minutes}m ago`
})
</script>