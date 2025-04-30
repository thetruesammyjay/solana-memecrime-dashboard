<template>
  <div class="space-y-2">
    <h3 class="text-sm font-semibold">Recent Alerts</h3>
    <div v-if="loading" class="flex justify-center py-4">
      <BaseSpinner size="sm" />
    </div>
    <div v-else class="space-y-2">
      <AlertCard 
        v-for="alert in alerts" 
        :key="alert.id" 
        :alert="alert" 
      />
    </div>
  </div>
</template>

<script setup>
import { useAlertsStore } from '@/stores/alerts'
import { storeToRefs } from 'pinia'

const { alerts, loading } = storeToRefs(useAlertsStore())
</script>