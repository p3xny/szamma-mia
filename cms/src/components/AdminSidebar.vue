<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api.js'

const router = useRouter()
const unreadOrderCount = ref(0)
const unreadReservationCount = ref(0)
let pollTimerOrd = null
let pollTimerRes = null


async function fetchUnreadCount(item) {
  try {
    const res = await api.get('/admin/notifications?unread_only=true')
    unreadOrderCount.value = res.data.filter(n => n.type === `order`).length
    unreadReservationCount.value = res.data.filter(n => n.type === `reservation`).length
  } catch { /* silent */ }
}

onMounted(() => {
  fetchUnreadCount('order')
  fetchUnreadCount('reservation')
  pollTimerOrd = setInterval(() => fetchUnreadCount('order'), 30000)
  pollTimerRes = setInterval(() => fetchUnreadCount('reservation'), 30000)
})

onUnmounted(() => {
  if (pollTimerOrd) clearInterval(pollTimerOrd)
  if (pollTimerRes) clearInterval(pollTimerRes)
})

function handleLogout() {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      Szamma <span>Mia</span>
      <small>CMS</small>
    </div>
    <nav class="sidebar-nav">
      <RouterLink to="/" class="sidebar-link" exact-active-class="active">
        Dashboard
      </RouterLink>
      <RouterLink to="/dishes" class="sidebar-link" active-class="active">
        Dania
      </RouterLink>
      <RouterLink to="/categories" class="sidebar-link" active-class="active">
        Kategorie
      </RouterLink>
      <RouterLink to="/coupons" class="sidebar-link" active-class="active">
        Kupony
      </RouterLink>
      <RouterLink to="/reservations" class="sidebar-link" active-class="active">
        Rezerwacje
        <span v-if="unreadReservationCount > 0" class="sidebar-badge">{{ unreadReservationCount }}</span>
      </RouterLink>
      <RouterLink to="/orders" class="sidebar-link" active-class="active">
        Zamówienia
        <span v-if="unreadOrderCount > 0" class="sidebar-badge">{{ unreadOrderCount }}</span>
      </RouterLink>
      <RouterLink to="/event-banners" class="sidebar-link" active-class="active">
        Banery
      </RouterLink>
      <RouterLink to="/settings" class="sidebar-link" active-class="active">
        Ustawienia
      </RouterLink>
    </nav>
    <button class="sidebar-logout" @click="handleLogout">Wyloguj</button>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--dark);
  color: var(--white);
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-brand {
  padding: 1.25rem 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--green);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-brand span {
  color: var(--red);
}

.sidebar-brand small {
  display: block;
  font-size: 0.7rem;
  font-weight: 400;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 0.15rem;
}

.sidebar-nav {
  flex: 1;
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
}

.sidebar-link {
  display: block;
  padding: 0.65rem 1rem;
  color: #bbb;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--white);
  text-decoration: none;
}

.sidebar-link {
  position: relative;
}

.sidebar-link.active {
  background: rgba(0, 146, 70, 0.15);
  color: var(--green);
  border-left: 3px solid var(--green);
}

.sidebar-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--red);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  margin-left: 0.5rem;
  line-height: 1;
}

.sidebar-logout {
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #999;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: color 0.2s;
}

.sidebar-logout:hover {
  color: var(--red);
}
</style>
