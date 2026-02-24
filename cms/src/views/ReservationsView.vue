<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const reservations = ref([])
const notifications = ref([])
const loading = ref(true)
const error = ref('')
const filterStatus = ref('')
const deleteTarget = ref(null)

const filtered = computed(() => {
  if (!filterStatus.value) return reservations.value
  return reservations.value.filter(r => r.status === filterStatus.value)
})

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

async function fetchData() {
  loading.value = true
  try {
    const [res, notifs] = await Promise.all([
      api.get('/admin/reservations'),
      api.get('/admin/notifications?unread_only=false'),
    ])
    reservations.value = res.data
    notifications.value = notifs.data.filter(n => n.type === 'reservation')
  } catch {
    error.value = 'Nie udało się załadować danych'
  } finally {
    loading.value = false
  }
}

async function cancelReservation(r) {
  try {
    await api.patch(`/admin/reservations/${r.id}`, { status: 'cancelled' })
    r.status = 'cancelled'
  } catch {
    error.value = 'Nie udało się anulować rezerwacji'
  }
}

async function confirmReservation(r) {
  try {
    await api.patch(`/admin/reservations/${r.id}`, { status: 'confirmed' })
    r.status = 'confirmed'
  } catch {
    error.value = 'Nie udało się przywrócić rezerwacji'
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/admin/reservations/${deleteTarget.value.id}`)
    deleteTarget.value = null
    await fetchData()
  } catch {
    error.value = 'Nie udało się usunąć rezerwacji'
    deleteTarget.value = null
  }
}

async function markNotifRead(n) {
  try {
    await api.patch(`/admin/notifications/${n.id}`)
    n.is_read = true
  } catch { /* silent */ }
}

async function markAllRead() {
  try {
    await api.post('/admin/notifications/read-all')
    notifications.value.forEach(n => { n.is_read = true })
  } catch { /* silent */ }
}

function formatDate(iso) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('T')[0].split('-')
  return `${d}.${m}.${y}`
}

// ── Phone helpers ──────────────────────────────────────────────────────────
const DIAL_FLAGS = {
  '+358': '🇫🇮', '+420': '🇨🇿', '+421': '🇸🇰', '+380': '🇺🇦', '+375': '🇧🇾',
  '+48': '🇵🇱', '+49': '🇩🇪', '+44': '🇬🇧', '+33': '🇫🇷', '+39': '🇮🇹',
  '+34': '🇪🇸', '+31': '🇳🇱', '+32': '🇧🇪', '+43': '🇦🇹', '+41': '🇨🇭',
  '+46': '🇸🇪', '+47': '🇳🇴', '+45': '🇩🇰', '+7': '🇷🇺', '+1': '🇺🇸',
}

function formatPhone(raw) {
  if (!raw) return '—'
  if (raw.startsWith('+')) return raw
  // Legacy entry without dial code — default to Polish +48
  const digits = raw.replace(/\D/g, '')
  return digits ? `+48 ${digits}` : raw
}

function phoneFlag(raw) {
  const normalized = formatPhone(raw)
  const dial = Object.keys(DIAL_FLAGS)
    .sort((a, b) => b.length - a.length)
    .find(d => normalized.startsWith(d))
  return dial ? DIAL_FLAGS[dial] : ''
}

function phoneHref(raw) {
  return 'tel:' + formatPhone(raw).replace(/\s/g, '')
}

onMounted(fetchData)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Rezerwacje</h1>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Notifications banner -->
    <div v-if="unreadCount > 0" class="card" style="border-left: 4px solid var(--green); margin-bottom: 1rem">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem">
        <strong>Nowe powiadomienia ({{ unreadCount }})</strong>
        <button class="btn btn-sm btn-secondary" @click="markAllRead">Oznacz jako przeczytane</button>
      </div>
      <div
        v-for="n in notifications.filter(x => !x.is_read)"
        :key="n.id"
        style="padding: 0.4rem 0; border-bottom: 1px solid #eee; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center"
      >
        <span>{{ n.message }}</span>
        <button class="btn btn-sm btn-secondary" @click="markNotifRead(n)" style="white-space: nowrap">OK</button>
      </div>
    </div>

    <!-- Filter -->
    <div class="card" style="padding: 0.75rem 1rem; margin-bottom: 1rem">
      <div style="display: flex; align-items: center; gap: 0.75rem">
        <label style="font-size: 0.85rem; font-weight: 600; white-space: nowrap">Status:</label>
        <select v-model="filterStatus" class="form-control" style="max-width: 200px">
          <option value="">Wszystkie</option>
          <option value="confirmed">Potwierdzone</option>
          <option value="cancelled">Anulowane</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div v-if="loading" class="card">Ładowanie...</div>
    <div v-else class="card table-wrap" style="padding: 0">
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Godzina</th>
            <th>Stolik</th>
            <th>Gość</th>
            <th>Telefon</th>
            <th>Osoby</th>
            <th>Status</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filtered" :key="r.id">
            <td>{{ formatDate(r.reservation_date) }}</td>
            <td>{{ r.start_time }}</td>
            <td><strong>{{ r.table_label }}</strong></td>
            <td>{{ r.guest_name }}</td>
            <td class="phone-cell">
              <span class="phone-flag">{{ phoneFlag(r.guest_phone) }}</span>
              <a :href="phoneHref(r.guest_phone)" class="phone-link">{{ formatPhone(r.guest_phone) }}</a>
            </td>
            <td>{{ r.guests_count }}</td>
            <td>
              <span class="badge" :class="r.status === 'confirmed' ? 'badge-green' : 'badge-red'">
                {{ r.status === 'confirmed' ? 'Potwierdzona' : 'Anulowana' }}
              </span>
            </td>
            <td>
              <div style="display: flex; gap: 0.3rem">
                <button
                  v-if="r.status === 'confirmed'"
                  class="btn btn-danger btn-sm"
                  @click="cancelReservation(r)"
                >Anuluj</button>
                <button
                  v-if="r.status === 'cancelled'"
                  class="btn btn-primary btn-sm"
                  @click="confirmReservation(r)"
                >Przywróć</button>
                <button class="btn btn-secondary btn-sm" @click="deleteTarget = r">Usuń</button>
              </div>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="8" style="text-align: center; color: #999">Brak rezerwacji</td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunąć rezerwację ${deleteTarget.guest_name} na ${deleteTarget.reservation_date}?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.phone-cell {
  white-space: nowrap;
}

.phone-flag {
  margin-right: 4px;
}

.phone-link {
  color: inherit;
  text-decoration: none;
  font-weight: 500;
}

.phone-link:hover {
  text-decoration: underline;
  color: var(--primary, #2563eb);
}
</style>
