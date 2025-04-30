<template>
  <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-solana-green" :class="sizeClass"></div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (val) => ['sm', 'md', 'lg'].includes(val)
  }
})

const sizeClass = computed(() => {
  return {
    sm: 'h-4 w-4 border-b',
    md: 'h-6 w-6 border-b-2',
    lg: 'h-8 w-8 border-b-4'
  }[props.size]
})
</script>