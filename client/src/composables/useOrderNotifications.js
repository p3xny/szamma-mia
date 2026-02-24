import { ref } from 'vue'
import { api } from './useApi'

// Module-level singletons so the state survives across component mounts
const notifications = ref([])  // { id, orderId, status, etaMinutes, message }
const polling = ref(false)
let pollTimer = null
let nextId = 1

const ACTIVE_STATUSES = new Set(['pending', 'confirmed', 'preparing', 'delivering'])
const POLL_INTERVAL_MS = 25000
const LS_KEY = 'order_status_seen'

const statusMessages = {
  confirmed: (o) => `Zamówienie #${o.id} potwierdzone!${o.eta_minutes ? ` Szacowany czas: ${o.eta_minutes} min.` : ''}`,
  preparing: (o) => `Zamówienie #${o.id} jest w przygotowaniu.`,
  delivering: (o) => `Zamówienie #${o.id} jest w drodze! 🛵`,
  completed: (o) => `Zamówienie #${o.id} zostało zrealizowane. Smacznego!`,
  cancelled: (o) => `Zamówienie #${o.id} zostało anulowane.`,
}

function loadSeen() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}') } catch { return {} }
}

function saveSeen(seen) {
  localStorage.setItem(LS_KEY, JSON.stringify(seen))
}

async function poll() {
  try {
    const res = await api.get('/my-orders')
    const orders = res.data
    const seen = loadSeen()
    const updated = { ...seen }

    for (const order of orders) {
      const prev = seen[order.id]
      const curr = order.status

      // First time we see this order — just record it, no notification
      if (prev === undefined) {
        updated[order.id] = curr
        continue
      }

      // Status changed
      if (prev !== curr) {
        updated[order.id] = curr
        const msgFn = statusMessages[curr]
        if (msgFn) {
          notifications.value.push({
            id: nextId++,
            orderId: order.id,
            status: curr,
            etaMinutes: order.eta_minutes,
            message: msgFn(order),
          })
        }
      }
    }

    saveSeen(updated)

    // Stop polling once all recent orders are terminal
    const hasActive = orders.some(o => ACTIVE_STATUSES.has(o.status))
    if (!hasActive) stopPolling()
  } catch {
    // silent — network error, keep polling
  }
}

function startPolling() {
  if (polling.value) return
  polling.value = true
  poll()  // immediate first check
  pollTimer = setInterval(poll, POLL_INTERVAL_MS)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  polling.value = false
}

function dismiss(notifId) {
  notifications.value = notifications.value.filter(n => n.id !== notifId)
}

function dismissAll() {
  notifications.value = []
}

export function useOrderNotifications() {
  return { notifications, startPolling, stopPolling, dismiss, dismissAll }
}
