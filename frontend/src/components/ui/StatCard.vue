<template>
    <BaseCard>
      <div class="text-center space-y-2">
        <h2 class="text-lg font-semibold">{{ title }}</h2>
        <p class="text-3xl font-bold" :class="colorClass">{{ value }}</p>
      </div>
    </BaseCard>
  </template>
  
  <script setup>
  import BaseCard from '@/components/ui/BaseCard.vue'
  
  defineProps({
    title: String,
    value: [String, Number],
    variant: {
      type: String,
      default: 'default' // 'default', 'warning', 'danger'
    }
  })
  
  const colorClass = computed(() => {
    switch (variant) {
      case 'warning':
        return 'text-yellow-400'
      case 'danger':
        return 'text-red-500'
      default:
        return 'text-white'
    }
  })
  </script>
  