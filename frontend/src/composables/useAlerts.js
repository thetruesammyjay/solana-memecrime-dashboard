import { ref, watch } from 'vue'
import { useAlertsStore } from '@/stores/alerts'

export function useAlerts() {
  const store = useAlertsStore()
  const unreadCount = ref(0)

  watch(() => store.alerts, (newAlerts) => {
    unreadCount.value = newAlerts.filter(a => !a.read).length
  }, { immediate: true })

  function markAsRead(alertId) {
    store.markAsRead(alertId)
  }

  return {
    alerts: computed(() => store.alerts),
    unreadCount,
    markAsRead
  }
}