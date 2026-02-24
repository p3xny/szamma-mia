<script setup>
import { ref, computed, provide, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'
import CartPanel from './components/CartPanel.vue'
import { useAuth } from '@/composables/useAuth'
import { useOrderNotifications } from '@/composables/useOrderNotifications'
import { usePushNotifications } from '@/composables/usePushNotifications'

const route = useRoute()
const hideNav = computed(() => ['/cart-summary', '/order-summary'].includes(route.path))

const cartOpen = ref(false)
const { fetchUser, isAuthenticated, isAdmin } = useAuth()
const { notifications, dismiss, startPolling, stopPolling } = useOrderNotifications()
const { subscribe, listenForForegroundPush } = usePushNotifications()

provide('openCart', () => { cartOpen.value = true })

onMounted(async () => {
  await fetchUser()
  if (isAuthenticated.value) startPolling()
  if (isAdmin.value) {
    listenForForegroundPush()   // play sound when push arrives in foreground
    await subscribe()           // register SW + request permission if needed
  }
})

// Start/stop polling as auth state changes; init push when admin logs in
watch(isAuthenticated, (val) => {
  if (val) startPolling()
  else stopPolling()
})

watch(isAdmin, async (val) => {
  if (val) {
    listenForForegroundPush()
    await subscribe()
  }
})

const statusIcons = {
  confirmed: '✅',
  preparing: '👨‍🍳',
  delivering: '🛵',
  completed: '🎉',
  cancelled: '❌',
}
</script>

<template>
  <NavBar v-if="!hideNav" @open-cart="cartOpen = true" />
  <RouterView />
  <CartPanel :isOpen="cartOpen" @close="cartOpen = false" />

  <!-- Global order notifications -->
  <Teleport to="body">
    <div class="order-notif-stack">
      <TransitionGroup name="notif">
        <div
          v-for="n in notifications"
          :key="n.id"
          class="order-notif"
          :class="`notif-${n.status}`"
        >
          <span class="notif-icon">{{ statusIcons[n.status] || '📦' }}</span>
          <span class="notif-msg">{{ n.message }}</span>
          <button class="notif-close" @click="dismiss(n.id)" aria-label="Zamknij">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style>
.order-notif-stack {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  align-items: center;
  z-index: 9000;
  pointer-events: none;
}

.order-notif {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #1a1a1a;
  color: #fff;
  padding: 0.75rem 1.1rem 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.22);
  pointer-events: all;
  max-width: 420px;
  width: max-content;
}

.notif-confirmed { border-left: 4px solid #009246; }
.notif-preparing { border-left: 4px solid #2563eb; }
.notif-delivering { border-left: 4px solid #2563eb; }
.notif-completed { border-left: 4px solid #009246; }
.notif-cancelled { border-left: 4px solid #ce2b37; }

.notif-icon { font-size: 1.1rem; flex-shrink: 0; }

.notif-msg { flex: 1; }

.notif-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.6);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 0.1rem;
  line-height: 1;
  flex-shrink: 0;
  transition: color 0.15s;
}
.notif-close:hover { color: #fff; }

.notif-enter-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.notif-leave-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.notif-enter-from  { opacity: 0; transform: translateY(12px); }
.notif-leave-to    { opacity: 0; transform: translateY(8px); }

@media (max-width: 480px) {
  .order-notif-stack {
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    transform: none;
    align-items: stretch;
  }
  .order-notif { max-width: 100%; width: auto; }
}
</style>
