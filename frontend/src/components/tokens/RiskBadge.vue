<template>
  <span class="px-2 py-1 rounded-full text-xs" :class="riskClasses">
    {{ riskText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  level: {
    type: String,
    default: 'low',
    validator: (val) => ['low', 'medium', 'high', 'critical'].includes(val)
  }
})

const riskText = computed(() => {
  return {
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical'
  }[props.level]
})

const riskClasses = computed(() => {
  return {
    low: 'bg-green-500/20 text-green-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    high: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400'
  }[props.level]
})
</script>