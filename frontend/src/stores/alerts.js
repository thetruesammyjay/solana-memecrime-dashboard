import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAlertsStore = defineStore('alerts', () => {
  const alerts = ref([])
  const loading = ref(false)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api'

  async function fetchAlerts() {
    loading.value = true
    try {
      const response = await fetch(`${API_URL}/alerts`)
      const data = await response.json()
      alerts.value = data.map(alert => ({
        ...alert,
        timestamp: new Date(alert.timestamp)
      }))
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
    } finally {
      loading.value = false
    }
  }

  async function createAlert(tokenAddress, type) {
    try {
      const response = await fetch(`${API_URL}/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tokenAddress,
          type,
          timestamp: new Date().toISOString()
        })
      })
      const newAlert = await response.json()
      alerts.value.unshift(newAlert)
    } catch (err) {
      console.error('Failed to create alert:', err)
    }
  }

  return {
    alerts,
    loading,
    fetchAlerts,
    createAlert
  }
})