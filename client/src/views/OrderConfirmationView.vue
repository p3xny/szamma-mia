<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrder } from '@/composables/useApi'

const route = useRoute()
const router = useRouter()

const order = ref(null)
const loading = ref(true)
const error = ref('')
const statusChanged = ref(false)
let pollTimer = null

const TERMINAL_STATUSES = new Set(['completed', 'cancelled'])
const POLL_INTERVAL_MS = 20000

const statusLabels = {
  pending: 'Oczekuje na potwierdzenie',
  confirmed: 'Potwierdzone',
  preparing: 'W przygotowaniu',
  delivering: 'W dostawie',
  completed: 'Zrealizowane',
  cancelled: 'Anulowane',
}

const statusIcons = {
  pending: '⏳',
  confirmed: '✅',
  preparing: '👨‍🍳',
  delivering: '🛵',
  completed: '🎉',
  cancelled: '❌',
}

const etaText = computed(() => {
  if (!order.value?.eta_minutes) return null
  return `${order.value.eta_minutes} min`
})

async function pollOrder() {
  try {
    const fresh = await getOrder(route.params.id)
    if (order.value && fresh.status !== order.value.status) {
      statusChanged.value = true
      setTimeout(() => { statusChanged.value = false }, 4000)
    }
    order.value = fresh
    if (TERMINAL_STATUSES.has(fresh.status)) stopPolling()
  } catch {
    // silent — keep polling
  }
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onMounted(async () => {
  try {
    order.value = await getOrder(route.params.id)
    if (!TERMINAL_STATUSES.has(order.value.status)) {
      pollTimer = setInterval(pollOrder, POLL_INTERVAL_MS)
    }
  } catch {
    error.value = 'Nie udało się pobrać zamówienia'
  } finally {
    loading.value = false
  }
})

onUnmounted(stopPolling)
</script>

<template>
  <div class="confirm-page">
    <div class="confirm-header">
      <button class="confirm-back" @click="router.push('/account')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>
        </svg>
        Moje zamówienia
      </button>
    </div>

    <div class="confirm-content">
      <div v-if="loading" class="confirm-loading">Ładowanie...</div>

      <div v-else-if="error" class="confirm-error">{{ error }}</div>

      <template v-else-if="order">
        <!-- Status change flash notification -->
        <Transition name="status-toast">
          <div v-if="statusChanged" class="status-toast">
            Status zamówienia został zaktualizowany
          </div>
        </Transition>

        <div class="confirm-icon" :class="{ 'icon-pulse': statusChanged }">
          <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>

        <h1 class="confirm-title">Zamówienie przyjęte</h1>
        <p class="confirm-id">Numer zamówienia: <strong>#{{ order.id }}</strong></p>
        <p class="confirm-status">
          <span class="status-icon">{{ statusIcons[order.status] || '' }}</span>
          Status: <span class="status-badge" :class="`status-${order.status}`">{{ statusLabels[order.status] || order.status }}</span>
        </p>

        <!-- ETA block — visible once order is confirmed -->
        <Transition name="eta-appear">
          <div v-if="etaText && order.status !== 'pending'" class="eta-block">
            <div class="eta-icon">🕐</div>
            <div class="eta-info">
              <span class="eta-label">Szacowany czas realizacji</span>
              <span class="eta-time">{{ etaText }}</span>
            </div>
          </div>
        </Transition>

        <div class="confirm-items">
          <h3>Pozycje zamówienia</h3>
          <div class="confirm-item" v-for="item in order.items" :key="item.id">
            <div class="confirm-item-row">
              <span class="confirm-item-name">
                {{ item.dish_name }}
                <span v-if="item.quantity > 1">x{{ item.quantity }}</span>
              </span>
              <span class="confirm-item-price">{{ item.item_total }} zł</span>
            </div>
          </div>
        </div>

        <div class="confirm-summary">
          <div class="confirm-summary-row">
            <span>Produkty</span>
            <span>{{ order.items_total }} zł</span>
          </div>
          <div v-if="order.discount > 0" class="confirm-summary-row discount">
            <span>Rabat</span>
            <span>-{{ order.discount }} zł</span>
          </div>
          <div class="confirm-summary-row total">
            <span>Razem</span>
            <strong>{{ order.total }} zł</strong>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.confirm-page {
  min-height: 100vh;
  background: var(--white);
  display: flex;
  flex-direction: column;
  padding-top: 60px;
}

.confirm-header {
  display: flex;
  align-items: center;
  padding: 0.9rem 2rem;
  background: var(--white);
  border-bottom: 1px solid #eee;
}

.confirm-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--green);
  cursor: pointer;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.confirm-back:hover {
  background: rgba(0, 146, 70, 0.08);
}

.confirm-content {
  max-width: 600px;
  width: 100%;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  text-align: center;
}

.confirm-loading {
  font-size: 1.1rem;
  color: #888;
  padding: 3rem 0;
}

.confirm-error {
  color: var(--red);
  font-size: 1.1rem;
  font-weight: 600;
  padding: 3rem 0;
}

.confirm-icon {
  color: var(--green);
  margin-bottom: 1.5rem;
}

.confirm-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 0.75rem;
}

.confirm-id {
  font-size: 1.1rem;
  color: #555;
  margin-bottom: 0.5rem;
}

.confirm-id strong {
  color: var(--dark);
}

.confirm-status {
  font-size: 1rem;
  color: #555;
  margin-bottom: 2.5rem;
}

.status-badge {
  display: inline-block;
  background: rgba(0, 146, 70, 0.1);
  color: var(--green);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.9rem;
}

.confirm-items {
  text-align: left;
  margin-bottom: 1.5rem;
}

.confirm-items h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.confirm-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.confirm-item:last-child {
  border-bottom: none;
}

.confirm-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.confirm-item-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--dark);
}

.confirm-item-price {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--dark);
}

.confirm-summary {
  text-align: left;
  border-top: 2px solid var(--dark);
  padding-top: 1rem;
}

.confirm-summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0;
  font-size: 0.95rem;
  color: #555;
}

.confirm-summary-row.discount {
  color: var(--green);
  font-weight: 600;
}

.confirm-summary-row.total {
  border-top: 1px solid #eee;
  padding-top: 0.75rem;
  margin-top: 0.5rem;
  font-size: 1.2rem;
}

.confirm-summary-row.total strong {
  color: var(--green);
  font-size: 1.3rem;
}

/* Status icon */
.status-icon {
  margin-right: 0.25rem;
}

/* Status badge variants */
.status-badge.status-pending {
  background: rgba(234, 179, 8, 0.12);
  color: #a16207;
}

.status-badge.status-confirmed {
  background: rgba(0, 146, 70, 0.1);
  color: var(--green);
}

.status-badge.status-preparing {
  background: rgba(59, 130, 246, 0.1);
  color: #1d4ed8;
}

.status-badge.status-delivering {
  background: rgba(59, 130, 246, 0.1);
  color: #1d4ed8;
}

.status-badge.status-completed {
  background: rgba(0, 146, 70, 0.1);
  color: var(--green);
}

.status-badge.status-cancelled {
  background: rgba(206, 43, 55, 0.08);
  color: var(--red);
}

/* ETA block */
.eta-block {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(0, 146, 70, 0.07);
  border: 1.5px solid rgba(0, 146, 70, 0.25);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin: 0 auto 2rem;
  max-width: 320px;
}

.eta-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.eta-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.eta-label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.eta-time {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--green);
}

/* Status change toast */
.status-toast {
  position: fixed;
  top: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  background: var(--green);
  color: #fff;
  padding: 0.65rem 1.5rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  z-index: 100;
  white-space: nowrap;
}

.status-toast-enter-active,
.status-toast-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.status-toast-enter-from,
.status-toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-12px);
}

/* ETA appear transition */
.eta-appear-enter-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.eta-appear-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

/* Icon pulse on status change */
@keyframes icon-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.12); }
}

.icon-pulse {
  animation: icon-pulse 0.6s ease;
}

@media (max-width: 600px) {
  .confirm-content {
    padding: 2rem 1rem;
  }

  .confirm-title {
    font-size: 1.5rem;
  }

  .confirm-header {
    padding: 0.75rem 1rem;
  }
}
</style>
